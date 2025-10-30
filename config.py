simulationTime = 39600 #time at the end of the simulation
startTime = 21600 #time at which the simulation starts
stepTime = 0.25 #length of the step
cooldownTime = 60 #length of the cooldown period
tram_to_tls_det_distance = 1.5 #distance away from tls, where trams get detected
red_min_duration_coefficient = 0.5 #minimum red duration coefficient

#print(tls_cooldown_status)


while traci.simulation.getTime() < 39600:
    traci.simulationStep()
    vehList = traci.vehicle.getIDList()
    tramList = list(filter(lambda x: "tram" in x, vehList))# Get all tramss
    for tram in tramList:
        tls_info = traci.vehicle.getNextTLS(tram)
        if not tls_info:
            continue 
        tlsID, tlsIndex, tram_to_tls_distance, tls_state = tls_info[0]
        if tram_to_tls_distance < 1.5: #check if the tram is next to the intersection (1.5 is just a value that worked)
            
            #print("tls_state", tls_state)
            #print("controlled_links",controlled_links)
            #print("next edge",next_edge)

            if tls_state not in ["R", "r"] or tls_cooldown_status[tlsID]["cooldown"]: #if the phase is yellow before green or green, we pass on to the next tram
                continue
            else:
                red_phase_duration = traci.trafficlight.getPhaseDuration(tlsID)
                red_spent_duration = traci.trafficlight.getSpentDuration(tlsID)
                if red_spent_duration < 0.5 * red_phase_duration:
                    continue
                else:
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
                    #stolen_time=traci.trafficlight.getNextSwitch(tlsID) - traci.simulation.getTime() #determine how much time we stole from the phase, from which we switched
                    stolen_tls_phase=traci.trafficlight.getPhase(tlsID) #what phase did we steal from
                    
                    tls_logics = traci.trafficlight.getAllProgramLogics(tlsID) #Here we get the definitions for all of the phases in the TLS program
                    tls_logic = tls_logics[0]
                    phases = tls_logic.phases
                    target_phase = None
                    
                    #original_stolen_phase_duration = phases[stolen_tls_phase].duration
                    #tls_cooldown_status[tlsID]["stolen_tls_phase"]= stolen_tls_phase
                    #tls_cooldown_status[tlsID]["originalcyclelength"]= original_stolen_phase_duration
                    #tls_cooldown_status[tlsID]["stolen_time"]= stolen_time
                    for phase_tls_order, phase in enumerate(phases):
                            if phase.state[tram_index] == "u":
                                target_phase = phase_tls_order
                                break
                                    
                    if target_phase is not None:
                        traci.trafficlight.setPhase(tlsID, target_phase)
                        next_phase_index = (phase_tls_order + 1) % len(phases)
                        tls_cooldown_status[tlsID]["yellow_before_benf_phase"]= phase_tls_order
                        tls_cooldown_status[tlsID]["benefited_tls_phase"]= next_phase_index
                        granted_time = phases[next_phase_index].duration 
                        tls_cooldown_status[tlsID]["cooldown"] = True
                        tls_cooldown_status[tlsID]["cooldown_time"] += -granted_time #this so that the 60 seconds actually cover the next cycle
                        
                    else:
                        error(tlsID, "is broken")
    step += 1
    
    ## Updating the cooldown for the TLS, 
    for tls_id, tls in tls_cooldown_status.items():  
        if tls["cooldown"]:
            #Compensating the stolen time, giving it back to the phase from which we stole it
            #if traci.trafficlight.getPhase(tls_id)==tls["stolen_tls_phase"]: 
                    #new_time=tls["originalcyclelength"]+tls["stolen_time"]
                    #traci.trafficlight.setPhaseDuration(tls_id, new_time)
                    #tls["originalcyclelength"]=0.0
                    #tls["stolen_tls_phase"]=None
            #Compensating the stolen time, taking away the granted time from the next green phase (had to do it, otherwise congestion)
            if tls["cooldown_time"] > 50:
                if traci.trafficlight.getPhase(tls_id)==tls["benefited_tls_phase"]:
                        traci.trafficlight.setPhaseDuration(tls_id, 0.0)
                        #tls["originalcyclelength"]=0.0
                        tls["benefited_tls_phase"]=None
                        print("skippedbenef")
                elif traci.trafficlight.getPhase(tls_id)==tls["yellow_before_benf_phase"]:
                        traci.trafficlight.setPhaseDuration(tls_id, 0.0)
                        #tls["originalcyclelength"]=0.0
                        tls["yellow_before_benf_phase"]=None
                        print("skippedyellowbefore")
            tls["cooldown_time"] += 1
            if tls["cooldown_time"] >= 80: #turn off the cooldown if the time lapsed is over 60 sec
                tls["cooldown"]=False
                tls["cooldown_time"]=0
                tls["stolen_time"]=0.0
                

    #print(tls_cooldown_status)
  
traci.close()

#traci.close()


