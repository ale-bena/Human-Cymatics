def _post_init_evacuation(sim):
    """Override all agents to target only exit POIs — simulates evacuation drill."""
    exit_pois = [p for p in sim.map_def['poi'] if p['category'] == 'exit']
    if not exit_pois:
        return
    for agent in sim.agents:
        agent.poi_list = exit_pois
        if hasattr(agent, '_goal_pois'):
            agent._goal_pois = exit_pois
        agent._pick_new_target()


SCENARIOS = {
    'baseline': {
        'n_people': 50,
        'sigma': 2.0,
        'behavior': 'wanderer',
        'post_init': None,
    },
    'concert_peak': {
        'n_people': 200,
        'sigma': 1.5,
        'behavior': 'social',
        'post_init': None,
    },
    'evacuation_drill': {
        'n_people': 150,
        'sigma': 2.0,
        'behavior': 'goal',
        'post_init': _post_init_evacuation,
    },
}
