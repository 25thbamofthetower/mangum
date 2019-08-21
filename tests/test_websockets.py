import mock
import pytest
from mangum import Mangum
from mangum.connections import ConnectionTable
from starlette.applications import Starlette
from starlette.websockets import WebSocket


def test_websocket_events(
    mock_ws_connect_event, mock_ws_send_event, mock_ws_disconnect_event, dynamodb
) -> None:

    table_name = "test-table"
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "connectionId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "connectionId", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    async def app(scope, receive, send):
        assert scope == {
            "client": ["192.168.100.1", 0],
            "headers": [
                [b"Accept-Encoding", b"gzip, deflate, br"],
                [b"Accept-Language", b"en-US,en;q=0.9"],
                [b"Cache-Control", b"no-cache"],
                [b"Host", b"test.execute-api.ap-southeast-1.amazonaws.com"],
                [b"Origin", b"https://test.execute-api.ap-southeast-1.amazonaws.com"],
                [b"Pragma", b"no-cache"],
                [
                    b"Sec-WebSocket-Extensions",
                    b"permessage-deflate; client_max_window_bits",
                ],
                [b"Sec-WebSocket-Key", b"bnfeqmh9SSPr5Sg9DvFIBw=="],
                [b"Sec-WebSocket-Version", b"13"],
                [
                    b"User-Agent",
                    b"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/"
                    b"537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                ],
                [b"X-Amzn-Trace-Id", b"Root=1-5d465cb6-78ddcac1e21f89203d004a89"],
                [b"X-Forwarded-For", b"192.168.100.1"],
                [b"X-Forwarded-Port", b"443"],
                [b"X-Forwarded-Proto", b"https"],
            ],
            "path": "/",
            "query_string": b"",
            "raw_path": None,
            "root_path": "Prod",
            "scheme": "https",
            "server": ["test.execute-api.ap-southeast-1.amazonaws.com", 80],
            "type": "websocket",
        }

        await send({"type": "websocket.accept", "subprotocol": None})
        await send({"type": "websocket.send", "text": "Hello world!"})
        await send({"type": "websocket.send", "bytes": b"Hello world!"})
        await send({"type": "websocket.close", "code": 1000})

    handler = Mangum(app, enable_lifespan=False)
    response = handler(mock_ws_connect_event, {})
    assert response == {
        "body": "OK",
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }

    handler = Mangum(app, enable_lifespan=False)
    with mock.patch(
        "mangum.protocols.websockets.ASGIWebSocketCycle.send_data"
    ) as send_data:
        send_data.return_value = None
        response = handler(mock_ws_send_event, {})
        assert response == {
            "body": "OK",
            "headers": {"content-type": "text/plain; charset=utf-8"},
            "isBase64Encoded": False,
            "statusCode": 200,
        }

    handler = Mangum(app, enable_lifespan=False)
    response = handler(mock_ws_disconnect_event, {})
    assert response == {
        "body": "OK",
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }


def test_websocket_cycle_state(
    mock_ws_connect_event, mock_ws_send_event, dynamodb
) -> None:
    table_name = "test-table"
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "connectionId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "connectionId", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    async def app(scope, receive, send):
        await send({"type": "websocket.send", "text": "Hello world!"})

    handler = Mangum(app, enable_lifespan=False)
    response = handler(mock_ws_connect_event, {})
    assert response == {
        "body": "OK",
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }

    handler = Mangum(app, enable_lifespan=False)

    with pytest.raises(RuntimeError):
        with mock.patch(
            "mangum.protocols.websockets.ASGIWebSocketCycle.send_data"
        ) as send_data:
            send_data.return_value = None
            handler(mock_ws_send_event, {})


def test_websocket_group_events(
    mock_ws_connect_event, mock_ws_send_event, mock_ws_disconnect_event, dynamodb
) -> None:

    table_name = "test-table"
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "connectionId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "connectionId", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    async def app(scope, receive, send):
        assert scope == {
            "client": ["192.168.100.1", 0],
            "headers": [
                [b"Accept-Encoding", b"gzip, deflate, br"],
                [b"Accept-Language", b"en-US,en;q=0.9"],
                [b"Cache-Control", b"no-cache"],
                [b"Host", b"test.execute-api.ap-southeast-1.amazonaws.com"],
                [b"Origin", b"https://test.execute-api.ap-southeast-1.amazonaws.com"],
                [b"Pragma", b"no-cache"],
                [
                    b"Sec-WebSocket-Extensions",
                    b"permessage-deflate; client_max_window_bits",
                ],
                [b"Sec-WebSocket-Key", b"bnfeqmh9SSPr5Sg9DvFIBw=="],
                [b"Sec-WebSocket-Version", b"13"],
                [
                    b"User-Agent",
                    b"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/"
                    b"537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                ],
                [b"X-Amzn-Trace-Id", b"Root=1-5d465cb6-78ddcac1e21f89203d004a89"],
                [b"X-Forwarded-For", b"192.168.100.1"],
                [b"X-Forwarded-Port", b"443"],
                [b"X-Forwarded-Proto", b"https"],
            ],
            "path": "/",
            "query_string": b"",
            "raw_path": None,
            "root_path": "Prod",
            "scheme": "https",
            "server": ["test.execute-api.ap-southeast-1.amazonaws.com", 80],
            "type": "websocket",
        }

        await send({"type": "websocket.accept", "subprotocol": None})
        await send(
            {"type": "websocket.send", "text": "Hello world!", "group": "testgroup"}
        )
        await send({"type": "websocket.close", "code": 1000})

    handler = Mangum(app, enable_lifespan=False)
    response = handler(mock_ws_connect_event, {})
    assert response == {
        "body": "OK",
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }

    handler = Mangum(app, enable_lifespan=False)
    with mock.patch(
        "mangum.protocols.websockets.ASGIWebSocketCycle.send_data"
    ) as send_data:
        send_data.return_value = None
        response = handler(mock_ws_send_event, {})
        assert response == {
            "body": "OK",
            "headers": {"content-type": "text/plain; charset=utf-8"},
            "isBase64Encoded": False,
            "statusCode": 200,
        }

    handler = Mangum(app, enable_lifespan=False)
    response = handler(mock_ws_disconnect_event, {})
    assert response == {
        "body": "OK",
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }


def test_websocket_get_group_items(dynamodb) -> None:
    table_name = "test-table"
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "connectionId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "connectionId", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    groups = ["test-group"]
    connection_table = ConnectionTable()
    connection_table.update_item("test1234", groups=groups)
    group_items = connection_table.get_group_items(groups[0])
    assert group_items[0]["connectionId"] == "test1234"


def test_starlette_websocket(
    mock_ws_connect_event, mock_ws_send_event, dynamodb
) -> None:
    table_name = "test-table"
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "connectionId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "connectionId", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    app = Starlette()

    @app.websocket_route("/ws")
    async def websocket_endpoint(websocket):
        await websocket.accept()
        await websocket.send_json({"url": str(websocket.url)})
        await websocket.close()

    handler = Mangum(app, enable_lifespan=False)
    response = handler(mock_ws_connect_event, {})
    assert response == {
        "body": "OK",
        "headers": {"content-type": "text/plain; charset=utf-8"},
        "isBase64Encoded": False,
        "statusCode": 200,
    }

    handler = Mangum(app, enable_lifespan=False)
    with mock.patch(
        "mangum.protocols.websockets.ASGIWebSocketCycle.send_data"
    ) as send_data:
        send_data.return_value = None
        response = handler(mock_ws_send_event, {})
        assert response == {
            "body": "OK",
            "headers": {"content-type": "text/plain; charset=utf-8"},
            "isBase64Encoded": False,
            "statusCode": 200,
        }
