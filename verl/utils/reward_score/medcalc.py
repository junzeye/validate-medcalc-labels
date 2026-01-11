import re, json
from typing import Dict, List, Union, Tuple, Optional
import datetime, logging
logger = logging.getLogger(__name__)


def parse_string_value(input_str: Union[str, float]) -> Tuple[Union[float, int, datetime.datetime, None], str]:
    """
    Parse a string and return (parsed_value, type_name). Could be used for both `extract_solution` and inside `compute_score` for extracting ground truth. Assumes that ``input_str`` is already stripped.
    
    Returns:
        Tuple of (parsed_value, type_string) where type_string is one of:
        'float', 'datetime', 'unknown', 'none'
    """
    # 0. Check if input_str is already a float or int
    if isinstance(input_str, float) or isinstance(input_str, int):
        return input_str, 'float'

    # 1. Try float pattern first (should also handle integer days)
    float_pattern = r'^-?\d+\.?\d*$' # -123.456, 123.456, 123, -123. "^" and "$" are for matching start and end of the string.
    if re.match(float_pattern, input_str):
        try:
            return float(input_str), 'float'
        except ValueError:
            logger.warning(f"Error parsing supposed float: {input_str}")
            return None, 'none'
        
    # 2. Try tuple with date units (Qwen would still output as week-day pairs, but the ground truth labels are already 
    # converted to days.)
    tuple_patterns = [
        r'^\(\s*(\d+)\s+weeks?,\s*(\d+)\s+days?\s*\)$',  # (X weeks, Y days)
        r'^\(\s*\'(\d+)\s+weeks?\'\s*,\s*\'(\d+)\s+days?\'\s*\)$',  # ('X weeks', 'Y days')
        r'^\(\s*(\d+)\s*,\s*(\d+)\s*\)$',  # (X, Y) - assume weeks, days
    ]
    for pattern in tuple_patterns:
        match = re.match(pattern, input_str, re.IGNORECASE)
        if match:
            try:
                weeks, days = map(int, match.groups())
                total_days = weeks * 7 + days
                return total_days, 'float' # inelegant fix to allow comparison with float - reconsider later
            except (ValueError, TypeError):
                logger.warning(f"Error parsing supposed week-days tuple: {input_str}")
                return None, 'none'

    # 3. See if output is "unknown"
    if input_str.lower() == "unknown":
        return "unknown", "unknown"
    # 4. Datetime formats
    try:
        # Use dateutil for flexible parsing
        from dateutil import parser as dateutil_parser
        parsed_date = dateutil_parser.parse(input_str)
        return parsed_date, 'datetime'
    except (ValueError, dateutil_parser.ParserError):
        logger.warning(f"Error parsing supposed datetime: {input_str}")
        return None, 'none'


def extract_solution(solution_str: str) -> Tuple[Union[float, int, datetime.datetime, None], str, str]:
    # Find the last <answer> tag position
    last_answer_pos = solution_str.rfind('<answer>')
    if last_answer_pos == -1:
        return None, 'none', 'ERROR: No <answer> tag found'
    # Look for </answer> after the last <answer>
    answer_content_start = last_answer_pos + len('<answer>')
    end_tag_pos = solution_str.find('</answer>', answer_content_start)
    if end_tag_pos == -1:
        return None, 'none', 'ERROR: No </answer> tag found'
    # Extract the content between the tags
    boxed_answer = solution_str[answer_content_start:end_tag_pos].strip()

    answer, answer_type = parse_string_value(boxed_answer)
    return answer, answer_type, boxed_answer


def compute_score(solution_str, ground_truth, data_source, format_score=0.1, full_score=1.0, **kwargs) -> Dict[str, float]:
    '''
    Args:
        solution_str: the answer given by the LLM (to be graded)
        ground_truth: verifiable reward, parsed from official MedCalc dataset.
        data_source: the source of the data - currently not used.
    Returns:
        a dictionary containing the score and other information.
    '''
    answer, answer_type, _ = extract_solution(solution_str=solution_str)
    # _ is the boxed answer, not used in computing score.
    
    if answer is None:  # Format error, unparsable.
        return {
            "score": 0.0,
            "acc": 0.0,
            "format_acc": 0.0
        }
    else:
        raw_lo, raw_hi = ground_truth[0], ground_truth[1]
        lo, lo_type = parse_string_value(raw_lo)
        hi, hi_type = parse_string_value(raw_hi)
        if any([lo_type == 'none', hi_type == 'none', answer_type != lo_type, answer_type != hi_type]):
            logger.warning(f"Incompatible answer type: answer_type: {answer_type}, lo_type: {lo_type}, hi_type: {hi_type}")
            return {
                "score": 0.0,
                "acc": 0.0,
                "format_acc": 0.0
            }
        # handle the case where the answer is "unknown"
        if any([answer_type == 'unknown', lo_type == 'unknown', hi_type == 'unknown']):
            if answer_type == lo_type == hi_type == 'unknown':
                return {
                    "score": full_score,
                    "acc": 1.0,
                    "format_acc": 1.0
                }
            else:
                return {
                    "score": format_score,
                    "acc": 0.0,
                    "format_acc": 1.0
                }
        if lo <= answer <= hi: # capable of handling float, days, and datetime
            return {
                "score": full_score,
                "acc": 1.0,
                "format_acc": 1.0
            }
        else:
            return {
                "score": format_score,
                "acc": 0.0,
                "format_acc": 1.0
            }


if __name__ == "__main__":
    solution_str = "blahblah<answer>123</answer>"
    ground_truth = ("unknown", "unknown")
    print(f"Solution: {solution_str}, Ground Truth: {ground_truth}")
    print(compute_score(solution_str, ground_truth, ''))

    solution_str = "blahblah<answer>(5 weeks, 6 days)</answer>"
    ground_truth = ("36.5", "40")
    print(f"Solution: {solution_str}, Ground Truth: {ground_truth}")
    print(compute_score(solution_str, ground_truth, ''))

    solution_str = "blahblah<answer>unknown</answer>"
    ground_truth = ("(5 weeks, 6 days)", "(5 weeks, 6 days)")
    print(f"Solution: {solution_str}, Ground Truth: {ground_truth}")
    print(compute_score(solution_str, ground_truth, ''))