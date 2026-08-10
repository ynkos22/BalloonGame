
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





# balloon_loop()

``` mermaid
flowchart TD
balloon["input = [balloon: Balloon]"]
player_loop{"For every strategy"}
action["strategy.action()"]
thresholds["thresholds: dict"]
resolve_round["resolve_round()"]
update_belief["strategy.update_belief()"]
sql_insert["sql_insert()"]

balloon --> player_loop
player_loop -- balloon: Balloon --> action -- threshold: int --> thresholds -- thresholds: dict[str, int] --> resolve_round -- obs_dict: dict[str, Observation] --> update_belief
resolve_round -- sql_list: list[tuple] --> sql_insert
player_loop -- balloon: Balloon --> resolve_round

```