from __future__ import annotations

import grpc

from . import inventory_pb2 as inventory__pb2


class InventoryServiceStub:
    def __init__(self, channel: grpc.Channel) -> None:
        self.CheckAndReserve = channel.unary_unary(
            "/shop.inventory.v1.InventoryService/CheckAndReserve",
            request_serializer=inventory__pb2.ReservationRequest.SerializeToString,
            response_deserializer=inventory__pb2.ReservationResponse.FromString,
        )
        self.ReleaseReservation = channel.unary_unary(
            "/shop.inventory.v1.InventoryService/ReleaseReservation",
            request_serializer=inventory__pb2.ReleaseRequest.SerializeToString,
            response_deserializer=inventory__pb2.ReleaseResponse.FromString,
        )


class InventoryServiceServicer:
    def CheckAndReserve(self, request, context):  # pragma: no cover - Interface
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def ReleaseReservation(self, request, context):  # pragma: no cover - Interface
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_InventoryServiceServicer_to_server(servicer, server) -> None:
    rpc_method_handlers = {
        "CheckAndReserve": grpc.unary_unary_rpc_method_handler(
            servicer.CheckAndReserve,
            request_deserializer=inventory__pb2.ReservationRequest.FromString,
            response_serializer=inventory__pb2.ReservationResponse.SerializeToString,
        ),
        "ReleaseReservation": grpc.unary_unary_rpc_method_handler(
            servicer.ReleaseReservation,
            request_deserializer=inventory__pb2.ReleaseRequest.FromString,
            response_serializer=inventory__pb2.ReleaseResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "shop.inventory.v1.InventoryService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))

