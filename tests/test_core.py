"""Tests for paper-verify."""

import pytest
from pathlib import Path
from paperverify.parser import LatexParser, Claim
from paperverify.matcher import ResultMatcher
from paperverify.validator import Validator, MatchStatus


class TestLatexParser:
    """Tests for LaTeX parser."""
    
    def test_parse_simple_number(self):
        parser = LatexParser()
        claims = parser.parse_content("The MAE is 2.44 on this dataset.")
        
        assert len(claims) >= 1
        values = [c.value for c in claims]
        assert 2.44 in values
    
    def test_parse_number_with_comma(self):
        parser = LatexParser()
        claims = parser.parse_content("Latency is 3,102ms.")
        
        values = [c.value for c in claims]
        assert 3102.0 in values
    
    def test_parse_k_suffix(self):
        parser = LatexParser()
        claims = parser.parse_content("Model has 98.5K parameters.")
        
        values = [c.value for c in claims]
        assert 98500.0 in values
    
    def test_parse_m_suffix(self):
        parser = LatexParser()
        claims = parser.parse_content("Model has 1.2M parameters.")
        
        values = [c.value for c in claims]
        assert 1200000.0 in values
    
    def test_identify_metric_mae(self):
        parser = LatexParser()
        claims = parser.parse_content("Achieves MAE of 2.10 on ETTh1.")
        
        mae_claims = [c for c in claims if c.metric_hint == 'mae']
        assert len(mae_claims) >= 1
    
    def test_identify_model_xgboost(self):
        parser = LatexParser()
        claims = parser.parse_content("XGBoost achieves 2.44 MAE.")
        
        xgb_claims = [c for c in claims if c.model_hint and 'xgboost' in c.model_hint]
        assert len(xgb_claims) >= 1
    
    def test_skip_comments(self):
        parser = LatexParser()
        claims = parser.parse_content("% This is a comment with 123\nReal text 456")
        
        values = [c.value for c in claims]
        assert 123.0 not in values
        assert 456.0 in values


class TestResultMatcher:
    """Tests for result matcher."""
    
    def test_find_exact_match(self):
        matcher = ResultMatcher()
        # Manually add a value
        from paperverify.matcher import ResultValue
        matcher.values.append(ResultValue(
            value=2.44,
            source_file="test.json",
            path="metrics.mae",
        ))
        matcher._build_index()
        
        matches = matcher.find_exact(2.44)
        assert len(matches) == 1
        assert matches[0].value == 2.44
    
    def test_find_close_match(self):
        matcher = ResultMatcher()
        from paperverify.matcher import ResultValue
        matcher.values.append(ResultValue(
            value=2.4404,
            source_file="test.json",
            path="metrics.mae",
        ))
        matcher._build_index()
        
        # 2.44 vs 2.4404 = 0.016% difference
        matches = matcher.find_matches(2.44, tolerance_pct=1.0)
        assert len(matches) == 1


class TestValidator:
    """Tests for validator."""
    
    def test_exact_match_status(self):
        matcher = ResultMatcher()
        from paperverify.matcher import ResultValue
        matcher.values.append(ResultValue(
            value=2.44,
            source_file="test.json",
            path="metrics.mae",
        ))
        matcher._build_index()
        
        validator = Validator(matcher)
        claim = Claim(
            value=2.44,
            raw_text="2.44",
            line_number=1,
            context="MAE of 2.44",
        )
        
        result = validator.verify_claim(claim)
        assert result.status == MatchStatus.EXACT_MATCH
    
    def test_close_match_status(self):
        matcher = ResultMatcher()
        from paperverify.matcher import ResultValue
        matcher.values.append(ResultValue(
            value=2.4404,
            source_file="test.json",
            path="metrics.mae",
        ))
        matcher._build_index()
        
        validator = Validator(matcher, tolerance_pct=1.0)
        claim = Claim(
            value=2.44,
            raw_text="2.44",
            line_number=1,
            context="MAE of 2.44",
        )
        
        result = validator.verify_claim(claim)
        assert result.status == MatchStatus.CLOSE_MATCH


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
