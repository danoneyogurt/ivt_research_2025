def genTLSdictionary():
    tls_ids = traci.trafficlight.getIDList()

    tls_cooldown_status = {
    tls_id: {"cooldown": False, "cooldown_time": 0.0, "stolen_tls_phase": None, "originalcyclelength":0.0, "stolen_time":0.0, "benefited_tls_phase": None, "yellow_before_benf_phase": None, "yellow_after" : None} #making a dictionary for each tls
    for tls_id in tls_ids
    }
    return tls_cooldown_status

def getTramList():
    vehList = traci.vehicle.getIDList()
    tramList = list(filter(lambda x: "tram" in x, vehList))# Get all tramss
    return tramList

def getTramInfo(tram)
    tls_info = traci.vehicle.getNextTLS(tram)
        if not tls_info:
            continue 
    tlsID, tlsIndex, tram_to_tls_distance, tls_state = tls_info[0]
    return tlsID, tlsIndex, tram_to_tls_distance, tls_state

def phaseSearch(tram,tlsID):
    tram_lane = traci.vehicle.getLaneID(tram)
    tram_route=traci.vehicle.getRoute(tram)
    current_edge = traci.vehicle.getRouteIndex(tram)
    next_edge = tram_route[current_edge + 1]
    controlled_links = traci.trafficlight.getControlledLinks(tlsID) #getting the lanes that are controlled by the tls
    tram_index = None

    for phase_index, link_pair in enumerate(controlled_links): #finding the correct index for the tram 
        for link in link_pair:
            if tram_lane == link[0] and next_edge in link[1]: #determining 
                tram_index = phase_index
                    break
            elif next_edge in link[0]: #this is for the cases when there is a very short edge right in front of the intersection
                next_edge=tram_route[current_edge + 2]
                if next_edge in link[1]:
                    tram_index = phase_index
                    break
    return tram_index
def phaseSearch2(tram_index, tlsID):
    tls_logics = traci.trafficlight.getAllProgramLogics(tlsID) #Here we get the definitions for all of the phases in the TLS program
                    tls_logic = tls_logics[0]
                    phases = tls_logic.phases
                    target_phase = None
                    for phase_tls_order, phase in enumerate(phases):
                            if phase.state[tram_index] == "u":
                                target_phase = phase_tls_order
                                break
    return target_phase, phases
def cooldownTurnon(tls_cooldown_status, target_phase, tlsID):
    tls_cooldown_status[tlsID]["yellow_before_benf_phase"]= phase_tls_order
    tls_cooldown_status[tlsID]["benefited_tls_phase"]= next_phase_index
    granted_time = phasls_cooldown_status, target_phase, tlsIDes[next_phase_index].duration 
    tls_cooldown_status[tlsID]["cooldown"] = True
    tls_cooldown_status[tlsID]["cooldown_time"] += -granted_time #this so that the 60 seconds actually cover the next cycle

def phaseChange(t):
    if target_phase is not None:
        traci.trafficlight.setPhase(tlsID, target_phase)
        next_phase_index = (target_phase + 1) % len(phases)
    else:
        error(tlsID, "is broken")
    return tls_cooldown_status

def tlsStateChange(tram):
        tlsID, tlsIndex, tram_to_tls_distance, tls_state = getTramInfo(tram)
        if tram_to_tls_distance < tram_to_tls_det_distance: #check if the tram is next to the intersection (1.5 is just a value that worked)

            if tls_state not in ["R", "r"] or tls_cooldown_status[tlsID]["cooldown"]: #if the phase is yellow before green or green, we pass on to the next tram
                continue
            else:
                red_phase_duration = traci.trafficlight.getPhaseDuration(tlsID)
                if red_spent_duration < red_min_duration_coefficient * red_phase_duration:
                    continue
                else:
                    tram_index = phaseSearch(tram, tlsID)
                    stolen_time=traci.trafficlight.getNextSwitch(tlsID) - traci.simulation.getTime() #determine how much time we stole from the phase, from which we switched
                    stolen_tls_phase=traci.trafficlight.getPhase(tlsID) #what phase did we steal from
                    
                    #original_stolen_phase_duration = phases[stolen_tls_phase].duration
                    #tls_cooldown_status[tlsID]["stolen_tls_phase"]= stolen_tls_phase
                    #tls_cooldown_status[tlsID]["originalcyclelength"]= original_stolen_phase_duration
                    #tls_cooldown_status[tlsID]["stolen_time"]= stolen_time
                    
                    target_phase, phases = phaseSearch2(tram_index, tlsID)
                                    
    return 