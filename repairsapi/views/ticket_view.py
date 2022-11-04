"""View module for handling requests for customer data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models.customer import Customer
from repairsapi.models.employee import Employee

from repairsapi.models.service_ticket import ServiceTicket


class TicketView(ViewSet):
    """Honey Rae API customers view"""

    def list(self, request):
        """Handle GET requests to get all customers

        Returns:
            Response -- JSON serialized list of customers
        """

        service_tickets = []

        if "status" in request.query_params: #In Django, the request object automatically has a property on it called query_params. It is a dictionary with the keys and values of all query params in the URL.
            if request.query_params['status'] == "done":
                service_tickets = ServiceTicket.objects.filter(date_completed__isnull=False)

            if request.query_params['status'] == "all":
                service_tickets = ServiceTicket.objects.all()

        else:
            service_tickets = ServiceTicket.objects.all()


        serialized = TicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single customer

        Returns:
            Response -- JSON serialized customer record
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        serialized = TicketSerializer(service_ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk = None):
        
        ticket = ServiceTicket.objects.get(pk=pk)

        employee_id = request.data['employee']

        assigned_employee = Employee.objects.get(pk=employee_id)

        ticket.employee = assigned_employee
        ticket.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk= None):

        ticket = ServiceTicket.objects.get(pk=pk)
        ticket.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class TicketCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id', 'address', 'full_name')


class TicketEmployeeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name')

class TicketSerializer(serializers.ModelSerializer):
    """JSON serializer for customers"""

    employee = TicketEmployeeeSerializer(many=False) #this ties the new employee model to this one

    customer = TicketCustomerSerializer(many=False)

    class Meta:
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description', 'emergency', 'date_completed')
        depth = 1 #adds on expansion