"""

"""
import json


class RequestParserProtocol:

    def on_message_begin():
        print(f"RequestParserProtocol - on_message_begin")

    def on_header(name: bytes, value: bytes):
        print(f"RequestParserProtocol - on_header(name, value) -> name: {name}, value: {value}")

    def on_headers_complete():
        print(f"RequestParserProtocol - on_headers_complete")

    def on_body(body: bytes):
        print(f"RequestParserProtocol - on_body(body) -> {body}")
        try:
            data = json.load(body.decode('utf-8'))
            print(f"data at RequestParserProtocol on_body(): {data}")
            return 200, data
        except Exception as e:
            print(f"exception at RequestParserProtocol on_body(): {e}")

    def on_message_complete():
        print(f"RequestParserProtocol - on_message_complete")

    def on_chunk_header():
        print(f"RequestParserProtocol - on_chunk_header")

    def on_chunk_complete():
        print(f"RequestParserProtocol - on_chunk_complete")
