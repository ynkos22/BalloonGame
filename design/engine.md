


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