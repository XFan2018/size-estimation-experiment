import csv
import heapq
import json
import math
import os
import statistics
from PIL import Image
import pandas as pd


def log_error(gt, estimate):
    return abs(math.log2(1 + estimate) - math.log2(1 + gt))


def signed_log_error(gt, estimate):
    return math.log2(1 + estimate) - math.log2(1 + gt)


def rel_error(gt, estimate):
    return abs(estimate - gt) / gt


def signed_rel_error(gt, estimate):
    return (estimate - gt) / gt


def process(gts, estimates, times, category):
    relative_errors = []
    signed_relative_errors = []

    log_errors = []
    signed_log_errors = []

    for gt, estimate in zip(gts, estimates):
        estimate = float(estimate)
        gt = float(gt)

        relative_errors.append(rel_error(gt, estimate))
        signed_relative_errors.append(signed_rel_error(gt, estimate))

        log_errors.append(log_error(gt, estimate))
        signed_log_errors.append(signed_log_error(gt, estimate))

    print(f"category: {category}")
    print(f"{len(gts)} data points")

    print("-" * 20 + "relative error" + "-" * 20)
    print(f"average time: {statistics.mean(times):.1f}")
    print(f"average relative error: {statistics.mean(relative_errors) * 100:.2f}%")
    print(f"median relative error: {statistics.median(relative_errors) * 100:.2f}%")
    print(f"std relative error: {statistics.stdev(relative_errors) * 100:.2f}%")
    print(f"average signed relative error: {statistics.mean(signed_relative_errors) * 100:.2f}%")
    print(f"median signed relative error: {statistics.median(signed_relative_errors) * 100:.2f}%")

    print("-" * 20 + "log error" + "-" * 20)
    print(f"average log error: {statistics.mean(log_errors) * 100:.2f}%")
    print(f"median log error: {statistics.median(log_errors) * 100:.2f}%")
    print(f"std log error: {statistics.stdev(log_errors) * 100:.2f}%")
    print(f"average signed log error: {statistics.mean(signed_log_errors) * 100:.2f}%")
    print(f"median signed log error: {statistics.median(signed_log_errors) * 100:.2f}%")
    print("\n\n")


def process_intermediate(categorys):
    for category in categorys:
        with open(f'states/{category}_saved_state.json', 'rb') as f:
            results = json.load(fp=f)
            responses = results["responses"]

            gts = []
            estimates = []
            for name, estimate, gt, time in responses:
                gts.append(gt)
                estimates.append(estimate)

            process(gts, estimates, category)


def process_final(categories):
    for category in categories:
        df = pd.read_csv(f"results/{category}_train.csv")

        gts = list(df["GT"])
        estimates = list(df["Response"])
        times = list(df["Time"])

        process(gts, estimates, times, category)
        # with open("xvolume/data/bird.txt", "r") as f:
        #     names = list(df["Image File"])
        #     for i, line in enumerate(f.readlines()):
        #         if line.strip() != names[i].split(".")[0].strip():
        #             print(line.strip(), names[i].split(".")[0].strip(), "error")


def process_intermediate_max_10(categorys):
    for category in categorys:
        relative_errors = []
        errors = []
        with open(f'states/{category}_saved_state.json', 'rb') as f:
            results = json.load(fp=f)
            responses = results["responses"][400:]

            for name, estimate, gt, time in responses:
                gt = float(gt)
                estimate = float(estimate)
                relative_error = rel_error(gt, estimate)
                signed_relative_error = signed_rel_error(gt, estimate)
                heapq.heappush(relative_errors, (-relative_error, name, signed_relative_error))
                errors.append(relative_error)

            nsmallest = heapq.nsmallest(10, relative_errors)
            # print(relative_errors)
            for element in nsmallest:
                print(f"{-element[0] * 100:.2f}%")
            for element in nsmallest:
                print(f"{element[2] * 100:.2f}%")
            for element in nsmallest:
                print(element[1].split(".")[0])


def write_json_to_csv(csv_file, json_file):
    with open(f'states/{json_file}.json', 'rb') as f:
        results = json.load(fp=f)
        responses = results["responses"]
        with open(os.path.join("results", csv_file) + ".csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Image File', 'Response', 'GT', 'Time'])  # Writing header
            for row in responses:
                writer.writerow(row)


if __name__ == "__main__":
    # process_intermediate(["bird"])
    process_final(["bird"])
    process_final(["dog"])
    # process_final(["cat"])
    # process_intermediate_max_10(["bird"])
