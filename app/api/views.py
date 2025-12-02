from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User, Order
from .serializers import UserSerializer, OrderSerializer
from django.shortcuts import get_object_or_404


# The swagger_auto_schema decorator is used to document the API endpoints.
@swagger_auto_schema(
    method="get",
    operation_summary="Lists all users or a single user by email",
    operation_description="API endpoint that retrieves all users or a single user by email and returns them in JSON "
    "format.",
    manual_parameters=[
        openapi.Parameter(
            "email",
            openapi.IN_QUERY,
            description="User is searched by this email and returned if found. Optional, if not "
            "present, all users are returned.",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={
        200: "One or all users in JSON format",
        400: "Bad request: Check error message for details",
        404: "If user was requested by email but not found",
        500: "Internal server error: Unexpected error",
    },
)
@api_view(["GET"])
def get_users(request):
    """
    API endpoint that retrieves all users or a single user by email.

    For retrieving all users, send a GET request without any parameters.

    For retrieving a single user, send a GET request with an "email" parameter
    that specifies the email address of the user to retrieve.

    :param request: A GET request object.
    :return: A JSON response with a list of all users or the requested user data.
             Returns an error response if the "email" parameter is missing or the
             requested user is not found.
    """

    # Return a single user if email parameter is provided
    if "email" in request.GET:
        email = request.GET["email"]

        # Check for empty email parameter
        if not email:
            return Response(
                {"result": "error", "message": "Email parameter is missing"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Return requested user
        try:
            user = get_object_or_404(User, email=email)
            serializer = UserSerializer(user)
            return Response(serializer.data)

        # Catch Http404 raised by get_object_or_404() if user is not found
        except Http404:
            return Response({"result": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Return all users
    try:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # Catch unexpected errors and return a 500 response
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    operation_summary="Creates new user",
    operation_description="API endpoint that creates a new user and returns the created user in JSON format.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the user"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email of the user"),
            "age": openapi.Schema(type=openapi.TYPE_INTEGER, description="Age of the user"),
        },
        required=["name", "email", "age"],
    ),
    responses={
        201: "Return the created user in JSON format",
        400: "Bad request: Check error message for details",
        500: "Internal server error: Unexpected error",
    },
)
@api_view(["POST"])
def add_user(request):
    """
    API endpoint that creates a new user and returns the created user in JSON format.

    :param request: POST request with name, email and age in JSON format
    :return: JSON response with newly created user or error message
    """

    # Try to create a new user
    try:
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)

    # Catch validation errors and return a 400 response
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    # Catch unexpected errors and return a 500 response
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="put",
    operation_summary="Updates existing user",
    operation_description="API endpoint that updates an existing users name and age by provided email and returns "
    "updated user in JSON format.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="Update the name of the user"),
            "age": openapi.Schema(type=openapi.TYPE_INTEGER, description="Update the age of the user"),
        },
        required=["name", "age"],
    ),
    manual_parameters=[
        openapi.Parameter(
            "email", openapi.IN_QUERY, description="Email of the user to update", type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: "Return the created user in JSON format",
        400: "Bad request: Check error message for details",
        404: "No user found with the provided email address",
        500: "Internal server error: Unexpected error",
    },
)
@api_view(["PUT"])
def update_user(request):
    """
    API endpoint that updates an existing users name and age by provided email.

    :param request: PUT request with user data and email parameter
    :return: JSON response with user data or error message
    """

    email = request.query_params.get("email")

    # Check for empty email parameter
    if not email:
        return Response(
            {"result": "error", "message": "Email parameter is missing"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Try to get the user by email
    try:
        user = get_object_or_404(User, email=email)
        # Ensure that the email address won"t be changed
        request_data = request.data.copy()
        request_data["email"] = email

    # Catch Http404 raised by get_object_or_404() if user is not found
    except Http404:
        return Response({"result": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Catch unexpected errors and return a 500 response
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Try to update the user
    try:
        serializer = UserSerializer(user, data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    # Catch validation errors and return a 400 response
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    # Catch unexpected errors and return a 500 response
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="delete",
    operation_summary="Deletes existing user",
    operation_description="API endpoint that deletes an existing user record by email",
    manual_parameters=[
        openapi.Parameter(
            "email", openapi.IN_QUERY, description="Email of the user to be deleted", type=openapi.TYPE_STRING
        )
    ],
    responses={
        204: "Success: User deleted",
        400: "Bad request: Check error message for details",
        404: "No user found with the provided email address",
        500: "Internal server error: Unexpected error",
    },
)
@api_view(["DELETE"])
def delete_user(request):
    """
    API endpoint that deletes an existing user record by email.

    :param request: DELETE request with email parameter as a query parameter in the URL
    :return: JSON response with success or error message
    """

    email = request.query_params.get("email")

    # Check for empty email parameter
    if not email:
        return Response(
            {"result": "error", "message": "Email parameter is missing"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Delete user
    try:
        user = get_object_or_404(User, email=email)
        user.delete()
        return Response({"result": "success", "message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)

    # Catch Http404 raised by get_object_or_404() if user is not found
    except Http404:
        return Response({"result": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Catch unexpected errors and return a 500 response
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="get",
    operation_summary="Lists all orders or a single order by id",
    operation_description="API endpoint that retrieves all orders or a single order by id and returns them in JSON format.",
    manual_parameters=[
        openapi.Parameter(
            "id",
            openapi.IN_QUERY,
            description="Order is searched by this id and returned if found. Optional, if not present, all orders are returned.",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={
        200: "One or all orders in JSON format",
        400: "Bad request: Check error message for details",
        404: "If order was requested by id but not found",
        500: "Internal server error: Unexpected error",
    },
)
@api_view(["GET"])
def get_orders(request):
    """API endpoint that retrieves all orders or a single order by id."""

    if "id" in request.GET:
        order_id = request.GET["id"]

        if not order_id:
            return Response(
                {"result": "error", "message": "Id parameter is missing"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = get_object_or_404(Order, id=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Http404:
            return Response({"result": "error", "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    operation_summary="Creates new order",
    operation_description="API endpoint that creates a new order and returns the created order in JSON format.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "user": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the user placing the order"),
            "phone_number": openapi.Schema(
                type=openapi.TYPE_STRING, description="Phone number of the user placing the order"
            ),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email of the user placing the order"),
            "products": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="List of products in the order",
                items=openapi.Items(type=openapi.TYPE_STRING),
            ),
            "price": openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL, description="Total price"),
        },
        required=["user", "phone_number", "email", "products", "price"],
    ),
    responses={
        201: "Return the created order in JSON format",
        400: "Bad request: Check error message for details",
        500: "Internal server error: Unexpected error",
    },
)
@api_view(["POST"])
def add_order(request):
    """API endpoint that creates a new order and returns the created order in JSON format."""

    try:
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="put",
    operation_summary="Updates existing order",
    operation_description="API endpoint that updates an existing order by provided id and returns the updated order in JSON format.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "user": openapi.Schema(type=openapi.TYPE_STRING, description="Update the name of the user"),
            "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description="Update the phone number"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="Update the email"),
            "products": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="Update the list of products",
                items=openapi.Items(type=openapi.TYPE_STRING),
            ),
            "price": openapi.Schema(
                type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL, description="Update the total price"
            ),
        },
        required=["user", "phone_number", "email", "products", "price"],
    ),
    manual_parameters=[
        openapi.Parameter(
            "id", openapi.IN_QUERY, description="Id of the order to update", type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: "Return the updated order in JSON format",
        400: "Bad request: Check error message for details",
        404: "No order found with the provided id",
        500: "Internal server error: Unexpected error",
    },
)
@api_view(["PUT"])
def update_order(request):
    """API endpoint that updates an existing order by provided id."""

    order_id = request.query_params.get("id")

    if not order_id:
        return Response(
            {"result": "error", "message": "Id parameter is missing"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        order = get_object_or_404(Order, id=order_id)
    except Http404:
        return Response({"result": "error", "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        serializer = OrderSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"result": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({"result": "error", "message": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="delete",
    operation_summary="Deletes existing order",
    operation_description="API endpoint that deletes an existing order record by id",
    manual_parameters=[
        openapi.Parameter(
            "id", openapi.IN_QUERY, description="Id of the order to be deleted", type=openapi.TYPE_STRING
        )
    ],
    responses={
        204: "Success: Order deleted",
        400: "Bad request: Check error message for details",
        404: "No order found with the provided id",
        500: "Internal server error: Unexpected error",
    },
)
@api_view(["DELETE"])
def delete_order(request):
    """API endpoint that deletes an existing order record by id."""

    order_id = request.query_params.get("id")

    if not order_id:
        return Response(
            {"result": "error", "message": "Id parameter is missing"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return Response({"result": "success", "message": "Order deleted"}, status=status.HTTP_204_NO_CONTENT)
    except Http404:
        return Response({"result": "error", "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
