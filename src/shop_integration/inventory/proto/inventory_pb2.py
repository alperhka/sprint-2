from __future__ import annotations

# Dieser Code wurde manuell aus dem gRPC IDL abgeleitet, um die Nutzung ohne protoc-Generator zu ermöglichen.
# Quelle: docs/proto/inventory.proto

from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

_sym_db = _symbol_database.Default()

_FILE_DESCRIPTOR_PROTO = _descriptor_pb2.FileDescriptorProto()
_FILE_DESCRIPTOR_PROTO.name = "inventory.proto"
_FILE_DESCRIPTOR_PROTO.package = "shop.inventory.v1"
_FILE_DESCRIPTOR_PROTO.syntax = "proto3"

# ReservationRequest
reservation_request = _FILE_DESCRIPTOR_PROTO.message_type.add()
reservation_request.name = "ReservationRequest"
field = reservation_request.field.add()
field.name = "order_id"
field.number = 1
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING
field = reservation_request.field.add()
field.name = "items"
field.number = 2
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
field.type_name = ".shop.inventory.v1.OrderItem"
field = reservation_request.field.add()
field.name = "reservation_ttl_seconds"
field.number = 3
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_INT32

# OrderItem
order_item = _FILE_DESCRIPTOR_PROTO.message_type.add()
order_item.name = "OrderItem"
field = order_item.field.add()
field.name = "product_id"
field.number = 1
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING
field = order_item.field.add()
field.name = "quantity"
field.number = 2
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_INT32

# ReservationResponse
reservation_response = _FILE_DESCRIPTOR_PROTO.message_type.add()
reservation_response.name = "ReservationResponse"
field = reservation_response.field.add()
field.name = "order_id"
field.number = 1
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING
field = reservation_response.field.add()
field.name = "status"
field.number = 2
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_ENUM
field.type_name = ".shop.inventory.v1.ReservationStatus"
field = reservation_response.field.add()
field.name = "reservation_id"
field.number = 3
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING
field = reservation_response.field.add()
field.name = "unavailable_items"
field.number = 4
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
field.type_name = ".shop.inventory.v1.UnavailableItem"
field = reservation_response.field.add()
field.name = "message"
field.number = 5
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING

# UnavailableItem
unavailable_item = _FILE_DESCRIPTOR_PROTO.message_type.add()
unavailable_item.name = "UnavailableItem"
field = unavailable_item.field.add()
field.name = "product_id"
field.number = 1
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING
field = unavailable_item.field.add()
field.name = "requested"
field.number = 2
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_INT32
field = unavailable_item.field.add()
field.name = "available"
field.number = 3
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_INT32

# ReleaseRequest
release_request = _FILE_DESCRIPTOR_PROTO.message_type.add()
release_request.name = "ReleaseRequest"
field = release_request.field.add()
field.name = "reservation_id"
field.number = 1
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING
field = release_request.field.add()
field.name = "order_id"
field.number = 2
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING

# ReleaseResponse
release_response = _FILE_DESCRIPTOR_PROTO.message_type.add()
release_response.name = "ReleaseResponse"
field = release_response.field.add()
field.name = "reservation_id"
field.number = 1
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING
field = release_response.field.add()
field.name = "success"
field.number = 2
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_BOOL
field = release_response.field.add()
field.name = "message"
field.number = 3
field.label = _descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
field.type = _descriptor_pb2.FieldDescriptorProto.TYPE_STRING

# ReservationStatus Enum
reservation_status = _FILE_DESCRIPTOR_PROTO.enum_type.add()
reservation_status.name = "ReservationStatus"
value = reservation_status.value.add()
value.name = "RESERVATION_STATUS_UNSPECIFIED"
value.number = 0
value = reservation_status.value.add()
value.name = "RESERVATION_STATUS_CONFIRMED"
value.number = 1
value = reservation_status.value.add()
value.name = "RESERVATION_STATUS_PARTIALLY_AVAILABLE"
value.number = 2
value = reservation_status.value.add()
value.name = "RESERVATION_STATUS_UNAVAILABLE"
value.number = 3

# InventoryService Definition
service = _FILE_DESCRIPTOR_PROTO.service.add()
service.name = "InventoryService"
method = service.method.add()
method.name = "CheckAndReserve"
method.input_type = ".shop.inventory.v1.ReservationRequest"
method.output_type = ".shop.inventory.v1.ReservationResponse"
method = service.method.add()
method.name = "ReleaseReservation"
method.input_type = ".shop.inventory.v1.ReleaseRequest"
method.output_type = ".shop.inventory.v1.ReleaseResponse"

DESCRIPTOR = _descriptor_pool.Default().Add(_FILE_DESCRIPTOR_PROTO)

ReservationStatus = DESCRIPTOR.enum_types_by_name["ReservationStatus"]

ReservationRequest = _reflection.GeneratedProtocolMessageType(
    "ReservationRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["ReservationRequest"],
        "__module__": "shop_integration.inventory.proto.inventory_pb2",
    },
)
_sym_db.RegisterMessage(ReservationRequest)

OrderItem = _reflection.GeneratedProtocolMessageType(
    "OrderItem",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["OrderItem"],
        "__module__": "shop_integration.inventory.proto.inventory_pb2",
    },
)
_sym_db.RegisterMessage(OrderItem)

ReservationResponse = _reflection.GeneratedProtocolMessageType(
    "ReservationResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["ReservationResponse"],
        "__module__": "shop_integration.inventory.proto.inventory_pb2",
    },
)
_sym_db.RegisterMessage(ReservationResponse)

UnavailableItem = _reflection.GeneratedProtocolMessageType(
    "UnavailableItem",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["UnavailableItem"],
        "__module__": "shop_integration.inventory.proto.inventory_pb2",
    },
)
_sym_db.RegisterMessage(UnavailableItem)

ReleaseRequest = _reflection.GeneratedProtocolMessageType(
    "ReleaseRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["ReleaseRequest"],
        "__module__": "shop_integration.inventory.proto.inventory_pb2",
    },
)
_sym_db.RegisterMessage(ReleaseRequest)

ReleaseResponse = _reflection.GeneratedProtocolMessageType(
    "ReleaseResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": DESCRIPTOR.message_types_by_name["ReleaseResponse"],
        "__module__": "shop_integration.inventory.proto.inventory_pb2",
    },
)
_sym_db.RegisterMessage(ReleaseResponse)

__all__ = [
    "OrderItem",
    "ReleaseRequest",
    "ReleaseResponse",
    "ReservationRequest",
    "ReservationResponse",
    "ReservationStatus",
    "UnavailableItem",
]

