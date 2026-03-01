import argparse
import csv
from collections import deque


class Request:
    def __init__(self, arrival_time, file_name, processing_time):
        self.arrival_time = int(arrival_time)
        self.file_name = file_name
        self.processing_time = int(processing_time)

    def get_arrival_time(self):
        return self.arrival_time

    def get_processing_time(self):
        return self.processing_time


class Server:
    def __init__(self):
        self.current_request = None
        self.time_remaining = 0

    def tick(self):
        if self.current_request:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.current_request = None

    def busy(self):
        return self.current_request is not None

    def start_next(self, request, current_time):
        self.current_request = request
        self.time_remaining = request.get_processing_time()
        return current_time - request.get_arrival_time()


def read_requests(filename):
    requests = []
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            arrival, file_name, processing = row
            requests.append(Request(arrival, file_name, processing))
    return requests


def simulate_one_server(filename):
    requests = read_requests(filename)
    request_queue = deque()
    server = Server()

    current_time = 0
    total_wait = 0
    processed = 0
    request_index = 0

    while request_index < len(requests) or server.busy() or request_queue:
        while (
            request_index < len(requests)
            and requests[request_index].get_arrival_time() == current_time
        ):
            request_queue.append(requests[request_index])
            request_index += 1

        if not server.busy() and request_queue:
            next_request = request_queue.popleft()
            wait_time = server.start_next(next_request, current_time)
            total_wait += wait_time
            processed += 1

        server.tick()
        current_time += 1

    avg_wait = total_wait / processed if processed > 0 else 0
    print(f"Average latency (1 server): {avg_wait:.2f} seconds")
    return avg_wait


def simulate_many_servers(filename, num_servers):
    requests = read_requests(filename)
    servers = [Server() for _ in range(num_servers)]
    queues = [deque() for _ in range(num_servers)]

    current_time = 0
    total_wait = 0
    processed = 0
    request_index = 0
    round_robin_counter = 0

    while request_index < len(requests) or any(
        server.busy() for server in servers
    ) or any(queues):
        while (
            request_index < len(requests)
            and requests[request_index].get_arrival_time() == current_time
        ):
            server_index = round_robin_counter % num_servers
            queues[server_index].append(requests[request_index])
            round_robin_counter += 1
            request_index += 1

        for i in range(num_servers):
            if not servers[i].busy() and queues[i]:
                next_request = queues[i].popleft()
                wait_time = servers[i].start_next(next_request, current_time)
                total_wait += wait_time
                processed += 1

            servers[i].tick()

        current_time += 1

    avg_wait = total_wait / processed if processed > 0 else 0
    print(f"Average latency ({num_servers} servers): {avg_wait:.2f} seconds")
    return avg_wait


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--servers", type=int)

    args = parser.parse_args()

    if args.servers:
        simulate_many_servers(args.file, args.servers)
    else:
        simulate_one_server(args.file)


if __name__ == "__main__":
    main()