import json
import statistics

relative_error = []
signed_relative_error = []

with open('states/dog_saved_state.json', 'rb') as f:
    results = json.load(fp=f)
    responses = results["responses"]
    n = len(responses)
    print(f"{n} data points")
    for name, estimate, gt, time in responses:
        estimate = float(estimate)
        gt = float(gt)
        relative_error.append(abs(estimate - gt) / gt)
        signed_relative_error.append((estimate - gt) / gt)

    print(f"average relative error: {statistics.mean(relative_error) * 100:.2f}%")
    print(f"median relative error: {statistics.median(relative_error) * 100:.2f}%")
    print(f"std relative error: {statistics.stdev(relative_error) * 100:.2f}%")
    print(f"average signed error: {statistics.mean(signed_relative_error) * 100:.2f}%")
    print(f"median signed error: {statistics.median(signed_relative_error) * 100:.2f}%")
