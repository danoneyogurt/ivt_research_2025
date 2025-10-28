import os
import sys



if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    from sumolib import checkBinary
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")



sumoBinary = "sumo-gui"
sumo_config_path = os.path.expanduser("~/Dokumente/SUMO_package/DODE_actuated.sumocfg")

if not os.path.exists(sumo_config_path):
    sys.exit(f"Error: Config file not found at {sumo_config_path}")

sumoCmd = [sumoBinary, "-c", sumo_config_path, "--start", "--quit-on-end"]


import traci
traci.start(sumoCmd)

step = 0
tls_ids = traci.trafficlight.getIDList()

tls_cooldown_status = {
    tls_id: {"cooldown": False, "cooldown_time": 0.0}
    for tls_id in tls_ids
}

##Same principle as with fixed, however no compensation for stolen time, we just skip to the tram phase. 
while step <= 39600:
    traci.simulationStep()
    vehList = traci.vehicle.getIDList()
    tramList = list(filter(lambda x: "tram" in x, vehList))# Get all tramss
    for tram in tramList:
        tls_info = traci.vehicle.getNextTLS(tram)
        if not tls_info:
            continue 
        tlsID, tlsIndex, tram_to_tls_distance, tls_state = tls_info[0]
        if tram_to_tls_distance < 1.5:
            tram_lane = traci.vehicle.getLaneID(tram)
            tram_route=traci.vehicle.getRoute(tram)
            current_edge = traci.vehicle.getRouteIndex(tram)
            next_edge = tram_route[current_edge + 1]

            controlled_links = traci.trafficlight.getControlledLinks(tlsID)
            tram_index = None
            #print("tls_state", tls_state)
            #print("controlled_links",controlled_links)
            #print("next edge",next_edge)

            if tls_state in ["G", "u"] or tls_cooldown_status[tlsID]["cooldown"]:
                #if tls_cooldown_status[tlsID]["cooldown"] == True:
                    #pass
                    #print("cooldown is on, priority not granted")
                    
                continue
            else:
                for phase_index, link_pair in enumerate(controlled_links): #finding the correct index for the tram 
                    for link in link_pair:
                        #print("links_what",link[0])
                        #print(phase_index)
                        if tram_lane == link[0] and next_edge in link[1]:
                            tram_index = phase_index
                            #print("Tram_index",tram_index)
                            break
                        elif next_edge in link[0]:
                            next_edge=tram_route[current_edge + 2]
                            if next_edge in link[1]:
                                tram_index = phase_index
                                #print("Tram_index",tram_index)
                                break
                stolen_time=traci.trafficlight.getNextSwitch(tlsID) - traci.simulation.getTime()
                #print(stolen_time)
                stolen_tls_phase=traci.trafficlight.getPhase(tlsID)
                
                tls_logics = traci.trafficlight.getAllProgramLogics(tlsID)
                tls_logic = tls_logics[0]
                phases = tls_logic.phases
                target_phase = None
                for phase_tls_order, phase in enumerate(phases):
                        #print(phase.state)
                        if phase.state[tram_index] == "u":
                            target_phase = phase_tls_order
                            #print(target_phase)
                            print("Success")
                            break
                            
                if target_phase is not None:
                    traci.trafficlight.setPhase(tlsID, target_phase)
                    tls_cooldown_status[tlsID]["cooldown"] = True
                    tls_cooldown_status[tlsID]["cooldown_time"] = 0.0

    step += 1
    # cooldown update
    for tls_id in tls_cooldown_status:
        if tls_cooldown_status[tls_id]["cooldown"]:
            tls_cooldown_status[tls_id]["cooldown_time"] += 1.0
            if tls_cooldown_status[tls_id]["cooldown_time"] >= 60.0:
                tls_cooldown_status[tls_id]["cooldown"] = False
                tls_cooldown_status[tls_id]["cooldown_time"] = 0.0



traci.close()

#traci.close()

