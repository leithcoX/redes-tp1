import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc
import time
import random
import argparse


class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):

    def __init__(self, delay_mean, delay_jitter, error_rate):
        self.delay_mean = delay_mean
        self.delay_jitter = delay_jitter
        self.error_rate = error_rate

    def Sumar(self, request, context):

        # Simulación de error probabilístico
        if random.random() < self.error_rate:
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Error simulado por el servidor"
            )

        # Cálculo del delay con jitter uniforme
        jitter = random.uniform(-self.delay_jitter, self.delay_jitter)
        delay_ms = max(0, self.delay_mean + jitter)

        time.sleep(delay_ms / 1000.0)

        resultado = request.a + request.b

        return calculator_pb2.SumarResponse(resultado=resultado)


def serve():
    parser = argparse.ArgumentParser(
        description="Servidor gRPC con delay, jitter y probabilidad de error"
    )
    parser.add_argument("delay_mean", type=float, help="Delay promedio en ms")
    parser.add_argument("delay_jitter", type=float, help="Jitter máximo en ms (+/-)")
    parser.add_argument("error_rate", type=float, help="Probabilidad de error (0.0 a 1.0)")
    parser.add_argument("--port", default=50051, type=int, help="Puerto del servidor")

    args = parser.parse_args()

    if not (0.0 <= args.error_rate <= 1.0):
        raise ValueError("error_rate debe estar entre 0.0 y 1.0")

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=100)
    )

    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(
            args.delay_mean,
            args.delay_jitter,
            args.error_rate
        ),
        server
    )

    server.add_insecure_port(f'[::]:{args.port}')
    server.start()

    print("Servidor gRPC iniciado")
    print(f"Puerto: {args.port}")
    print(f"Delay medio: {args.delay_mean} ms")
    print(f"Jitter: ±{args.delay_jitter} ms")
    print(f"Probabilidad de error: {args.error_rate}")

    server.wait_for_termination()


if __name__ == '__main__':
    serve()