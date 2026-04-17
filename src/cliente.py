import grpc
import calculator_pb2
import calculator_pb2_grpc


def run():
    channel = grpc.insecure_channel('[::1]:50051')
    stub = calculator_pb2_grpc.CalculatorStub(channel)

    a = 10
    b = 25

    request = calculator_pb2.SumarRequest(a=a, b=b)
    response = stub.Sumar(request)

    print(f"{a} + {b} = {response.resultado}")


if __name__ == "__main__":
    run()
