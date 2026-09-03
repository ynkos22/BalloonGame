
# resolve_round()
``` mermaid
flowchart TD


input["input = [thresholds: dict, balloon: Balloon]"]
payout["calc_payout()"]
update_PnL["update_PnL()"]
sql_parser["sql_parser()"]
obs_parser["obs_parser()"]
end_tuple["return_tuple"]


input -- input --> payout
payout -- dict[str, int] --> update_PnL --dict[str, int]--> sql_parser
payout --dict[str, int] --> obs_parser
input -- thresholds: dict --> obs_parser
input -- input --> sql_parser
input -- input --> obs_parser
obs_parser -- dict[str, Observation] --> end_tuple
sql_parser -- list[tuple] --> end_tuple
```
