import os
import sys
import traci


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    from sumolib import checkBinary
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

if not os.path.exists(sumo_config_path):
    sys.exit(f"Error: Config file not found at {sumo_config_path}")




traci.start(sumoCmd)


traci.start(sumoCmd)
step = 0

tls_cooldown_status = genTLSdictionary()

while traci.simulation.getTime() < simulationTime:
    traci.simulationStep()

    tramList = getTramList()
    for tram in tramList:
        tls_cooldown_status = tlsStateChange(tram, tls_cooldown_status)
        tls_cooldown_status = cooldownUpdate(tls_cooldown_status)
        step += 1


traci.close()

