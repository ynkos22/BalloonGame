import yaml


with open("temp.yaml") as f:
    cfg = yaml.safe_load(f)


print(cfg)