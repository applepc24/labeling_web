import requests
import config


def send_slack_message(message: str) -> bool:
    if not config.SLACK_WEBHOOK_URL:
        return False
    try:
        response = requests.post(
            config.SLACK_WEBHOOK_URL,
            json={"text": message},
            timeout=5,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def notify_detection_complete(video_name: str, high_count: int, low_count: int) -> bool:
    msg = (
        f"*[탐지 완료]* `{video_name}`\n"
        f"• 고신뢰도 탐지: {high_count}건\n"
        f"• 저신뢰도 탐지: {low_count}건 (threshold < {config.CONFIDENCE_THRESHOLD})"
    )
    return send_slack_message(msg)


def notify_pipeline_error(video_name: str, error: str, retry_count: int) -> bool:
    msg = (
        f"*[파이프라인 오류]* `{video_name}`\n"
        f"• 오류: {error}\n"
        f"• 재시도: {retry_count}/{config.MAX_RETRY}"
    )
    return send_slack_message(msg)
