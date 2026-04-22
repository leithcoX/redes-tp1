import grpc
import calculator_pb2
import calculator_pb2_grpc
import random
import time
import argparse
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


def call_sum(stub, a, b):
    start = time.perf_counter()

    try:
        request = calculator_pb2.SumarRequest(a=a, b=b)
        response = stub.Sumar(request)

        end = time.perf_counter()
        rtt_ms = (end - start) * 1000

        return {
            "a": a,
            "b": b,
            "resultado": response.resultado,
            "rtt": rtt_ms,
            "status": "OK"
        }

    except grpc.RpcError as e:
        end = time.perf_counter()
        rtt_ms = (end - start) * 1000

        return {
            "a": a,
            "b": b,
            "resultado": None,
            "rtt": rtt_ms,
            "status": e.code().name
        }


def main():
    parser = argparse.ArgumentParser(description="Cliente gRPC paralelo con estadísticas")
    parser.add_argument("threads", type=int, help="Cantidad de threads paralelos")
    parser.add_argument("--host", default="localhost:50051", help="Servidor host:puerto")

    args = parser.parse_args()

    channel = grpc.insecure_channel(args.host)
    stub = calculator_pb2_grpc.CalculatorStub(channel)

    futures = []
    rtts = []
    error_count = 0

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for _ in range(args.threads):
            a = random.randint(1, 1000)
            b = random.randint(1, 1000)
            futures.append(executor.submit(call_sum, stub, a, b))

        for future in as_completed(futures):
            result = future.result()

            a = result["a"]
            b = result["b"]
            rtt = result["rtt"]
            status = result["status"]

            if status == "OK":
                rtts.append(rtt)
                print(f"{a} + {b} = {result['resultado']} | "
                      f"RTT = {rtt:.3f} ms | status = {status}")
            else:
                error_count += 1
                print(f"{a} + {b} = ERROR | "
                      f"RTT = {rtt:.3f} ms | status = {status}")

    print("\n--- Estadísticas RTT ---")
    print(f"Cantidad total de requests: {len(futures)}")
    print(f"Errores: {error_count}")

    if len(rtts) > 0:
        mean_rtt = statistics.mean(rtts)
        std_rtt = statistics.stdev(rtts) if len(rtts) > 1 else 0.0

        print(f"RTT medio (exitosos): {mean_rtt:.3f} ms")
        print(f"Desvío estándar: {std_rtt:.3f} ms")
    else:
        print("No hubo requests exitosos")


if __name__ == "__main__":
    main()