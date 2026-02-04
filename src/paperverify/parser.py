"""LaTeX parser to extract numeric claims from paper files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Claim:
    """A numeric claim extracted from the paper."""
    
    value: float
    raw_text: str
    line_number: int
    context: str  # Surrounding text for matching
    metric_hint: Optional[str] = None  # e.g., "MAE", "latency"
    model_hint: Optional[str] = None  # e.g., "XGBoost", "Chronos"


class LatexParser:
    """Extract numeric claims from LaTeX files."""
    
    # Patterns for common numeric formats
    NUMERIC_PATTERNS = [
        # Decimal numbers: 2.44, 0.00013, 3102.32
        r'(\d+\.\d+)',
        # Integers with commas: 3,102
        r'(\d{1,3}(?:,\d{3})+)',
        # Plain integers: 60, 328
        r'(\d+)',
    ]
    
    # Metric keywords to identify what's being measured
    METRIC_KEYWORDS = {
        'mae': ['mae', 'mean absolute error'],
        'rmse': ['rmse', 'root mean squared error'],
        'smape': ['smape', 'symmetric mean absolute percentage'],
        'latency': ['latency', 'ms', 'millisecond', 'inference time'],
        'vram': ['vram', 'memory', 'gb'],
        'accuracy': ['accuracy', 'acc'],
    }
    
    # Model name patterns
    MODEL_PATTERNS = [
        r'xgboost',
        r'arima',
        r'chronos[\-\s]*(tiny|mini|small|large)?',
        r'moirai[\-\s]*(small|base|large)?',
        r'dlinear',
        r'patchtst',
        r'timesfm',
    ]
    
    def __init__(self):
        # Compile regex patterns
        self.number_pattern = re.compile(
            r'(?:^|[^\d])(' + '|'.join(self.NUMERIC_PATTERNS) + r')(?:[^\d]|$)',
            re.IGNORECASE
        )
        self.model_pattern = re.compile(
            '|'.join(self.MODEL_PATTERNS),
            re.IGNORECASE
        )
    
    def parse_file(self, filepath: Path) -> List[Claim]:
        """Parse a LaTeX file and extract numeric claims."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        content = filepath.read_text(encoding='utf-8')
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> List[Claim]:
        """Parse LaTeX content and extract numeric claims."""
        claims = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Skip comments
            if line.strip().startswith('%'):
                continue
            
            # Skip certain LaTeX commands
            if self._is_non_claim_line(line):
                continue
            
            # Extract numbers from this line
            line_claims = self._extract_claims_from_line(line, line_num)
            claims.extend(line_claims)
        
        return claims
    
    def _is_non_claim_line(self, line: str) -> bool:
        """Check if line should be skipped (package imports, etc.)."""
        skip_patterns = [
            r'\\usepackage',
            r'\\documentclass',
            r'\\bibliography',
            r'\\label{',
            r'\\ref{',
            r'\\cite',
        ]
        return any(re.search(p, line) for p in skip_patterns)
    
    def _extract_claims_from_line(self, line: str, line_num: int) -> List[Claim]:
        """Extract all numeric claims from a single line."""
        claims = []
        
        # Find all numbers in the line (including K/M/B suffixes when standalone)
        # Use lookahead to avoid capturing 'm' from 'ms', 'mb', etc.
        for match in re.finditer(r'[\d,]+\.?\d*(?:[KMB](?![a-z]))?', line, re.IGNORECASE):
            raw_text = match.group()
            
            # Skip very short numbers (likely page numbers, etc.)
            if len(raw_text) < 2 and '.' not in raw_text:
                continue
            
            # Parse the value
            try:
                value = self._parse_number(raw_text)
            except ValueError:
                continue
            
            # Skip unreasonable values (allow up to 1 billion for parameter counts)
            if value == 0 or value > 1_000_000_000:
                continue
            
            # Get context (surrounding text)
            start = max(0, match.start() - 50)
            end = min(len(line), match.end() + 50)
            context = line[start:end]
            
            # Try to identify metric type
            metric_hint = self._identify_metric(context)
            
            # Try to identify model
            model_hint = self._identify_model(context)
            
            claims.append(Claim(
                value=value,
                raw_text=raw_text,
                line_number=line_num,
                context=context,
                metric_hint=metric_hint,
                model_hint=model_hint,
            ))
        
        return claims
    
    def _parse_number(self, raw_text: str) -> float:
        """Parse a number string, handling commas and K/M/B suffixes."""
        cleaned = raw_text.replace(',', '').strip()
        
        # Handle K/M/B suffixes (e.g., 98.5K, 1.2M, 710M)
        multipliers = {
            'k': 1_000,
            'm': 1_000_000,
            'b': 1_000_000_000,
        }
        
        suffix = cleaned[-1].lower() if cleaned else ''
        if suffix in multipliers:
            numeric_part = cleaned[:-1]
            return float(numeric_part) * multipliers[suffix]
        
        return float(cleaned)
    
    def _identify_metric(self, context: str) -> Optional[str]:
        """Identify what metric is being reported."""
        context_lower = context.lower()
        for metric, keywords in self.METRIC_KEYWORDS.items():
            if any(kw in context_lower for kw in keywords):
                return metric
        return None
    
    def _identify_model(self, context: str) -> Optional[str]:
        """Identify what model is being discussed."""
        match = self.model_pattern.search(context)
        if match:
            return match.group().lower()
        return None


def parse_latex(filepath: Path) -> List[Claim]:
    """Convenience function to parse a LaTeX file."""
    parser = LatexParser()
    return parser.parse_file(filepath)
