import grpc
from concurrent import futures
import time

import calculator_pb2
import calculator_pb2_grpc


class CalculatorService(calculator_pb2_grpc.CalculatorServicer):

    def Sumar(self, request, context):
        print(f"Recibido: a={request.a}, b={request.b}")
        resultado = request.a + request.b
        return calculator_pb2.SumarResponse(resultado=resultado)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))

    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorService(), server
    )

    server.add_insecure_port('[::1]:50051')
    server.start()

    print("Servidor gRPC escuchando en puerto 50051...")

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Apagando servidor...")
        server.stop(0)


if __name__ == "__main__":
    serve()
