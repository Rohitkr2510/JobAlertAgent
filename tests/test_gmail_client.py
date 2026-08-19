import base64
from email.message import EmailMessage

from jobalert.gmail_client import build_query, decode_raw_message, iter_message_ids


class Execute:
    def __init__(self, response):
        self.response = response

    def execute(self):
        return self.response


class Messages:
    def list(self, **kwargs):
        if kwargs.get("pageToken") is None:
            return Execute({"messages": [{"id": "one"}], "nextPageToken": "next"})
        return Execute({"messages": [{"id": "two"}]})


class Users:
    def messages(self):
        return Messages()


class Service:
    def users(self):
        return Users()


def test_query_and_pagination() -> None:
    query = build_query(24, ["linkedin.com", "indeed.com"])
    assert query == "newer_than:1d (from:(linkedin.com) OR from:(indeed.com))"
    assert list(iter_message_ids(Service(), query)) == ["one", "two"]


def test_decode_raw_message_without_padding() -> None:
    message = EmailMessage()
    message["Subject"] = "DevOps jobs"
    message.set_content("hello")
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode().rstrip("=")
    assert decode_raw_message(raw)["Subject"] == "DevOps jobs"
