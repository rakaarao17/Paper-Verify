"""Validator to compare paper claims against result values."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .parser import Claim
from .matcher import ResultMatcher, ResultValue


class MatchStatus(Enum):
    """Status of a claim verification."""
    EXACT_MATCH = "exact"
    CLOSE_MATCH = "close"
    MISMATCH = "mismatch"
    UNVERIFIED = "unverified"


@dataclass
class VerificationResult:
    """Result of verifying a single claim."""
    
    claim: Claim
    status: MatchStatus
    matched_value: Optional[ResultValue] = None
    difference_pct: Optional[float] = None
    message: str = ""


class Validator:
    """Validate paper claims against experiment results."""
    
    def __init__(self, matcher: ResultMatcher, tolerance_pct: float = 1.0):
        """
        Initialize validator.
        
        Args:
            matcher: ResultMatcher with loaded results
            tolerance_pct: Percentage tolerance for "close" matches
        """
        self.matcher = matcher
        self.tolerance_pct = tolerance_pct
    
    def verify_claim(self, claim: Claim) -> VerificationResult:
        """Verify a single claim against results."""
        
        # First, try exact match
        exact_matches = self.matcher.find_exact(claim.value)
        if exact_matches:
            best_match = self._select_best_match(claim, exact_matches)
            return VerificationResult(
                claim=claim,
                status=MatchStatus.EXACT_MATCH,
                matched_value=best_match,
                difference_pct=0.0,
                message=f"Exact match in {best_match.source_file}",
            )
        
        # Try close match within tolerance
        close_matches = self.matcher.find_matches(claim.value, self.tolerance_pct)
        if close_matches:
            best_match = self._select_best_match(claim, close_matches)
            diff_pct = abs(best_match.value - claim.value) / abs(best_match.value) * 100
            return VerificationResult(
                claim=claim,
                status=MatchStatus.CLOSE_MATCH,
                matched_value=best_match,
                difference_pct=diff_pct,
                message=f"Close match ({diff_pct:.1f}% diff) in {best_match.source_file}",
            )
        
        # Try wider tolerance (5%) to find potential mismatches
        wide_matches = self.matcher.find_matches(claim.value, 10.0)
        if wide_matches:
            best_match = self._select_best_match(claim, wide_matches)
            diff_pct = abs(best_match.value - claim.value) / abs(best_match.value) * 100
            return VerificationResult(
                claim=claim,
                status=MatchStatus.MISMATCH,
                matched_value=best_match,
                difference_pct=diff_pct,
                message=f"Mismatch! Actual value is {best_match.value} ({diff_pct:.1f}% diff)",
            )
        
        # No match found
        return VerificationResult(
            claim=claim,
            status=MatchStatus.UNVERIFIED,
            message="No matching value found in results",
        )
    
    def verify_all(self, claims: List[Claim]) -> List[VerificationResult]:
        """Verify all claims."""
        return [self.verify_claim(c) for c in claims]
    
    def _select_best_match(
        self, 
        claim: Claim, 
        matches: List[ResultValue]
    ) -> ResultValue:
        """Select the best matching result value."""
        if len(matches) == 1:
            return matches[0]
        
        # Score matches based on context alignment
        scored = []
        for match in matches:
            score = 0
            
            # Metric match
            if claim.metric_hint and match.metric:
                if claim.metric_hint.lower() == match.metric.lower():
                    score += 10
            
            # Model match
            if claim.model_hint and match.model:
                if claim.model_hint.lower() in match.model.lower():
                    score += 10
                elif match.model.lower() in claim.model_hint.lower():
                    score += 10
            
            # Path contains relevant keywords
            if claim.metric_hint and claim.metric_hint.lower() in match.path.lower():
                score += 5
            
            scored.append((score, match))
        
        # Return highest scored match
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]


def verify_paper(
    claims: List[Claim],
    matcher: ResultMatcher,
    tolerance_pct: float = 1.0
) -> List[VerificationResult]:
    """Convenience function to verify all claims."""
    validator = Validator(matcher, tolerance_pct)
    return validator.verify_all(claims)
