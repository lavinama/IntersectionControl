#!/usr/bin/env python errors 

# To make sure that this file runs correctly without relative import module errors, write:
# export PYTHONPATH=/home/mario/Individual/IntersectionControl

import logging

from intersection_control.algorithms.stip.stip_vehicle import STIPVehicle
from intersection_control.algorithms.traffic_light.tl_intersection_manager import TLIntersectionManager
from intersection_control.algorithms.traffic_light.tl_vehicle import TLVehicle
from intersection_control.communication import DistanceBasedUnit
from intersection_control.environments.sumo import SumoEnvironment, RandomDemandGenerator
from intersection_control.algorithms.qb_im import QBIMIntersectionManager, QBIMVehicle
from intersection_control.environments.sumo.networks.single_intersection.demand_generators import \
    ConflictingDemandGenerator
from misc.utils import SINGLE_INTERSECTION_TL_PHASES

STEP_COUNT = 360000  # 1 Hour

im_factory = {
    "qb_im": lambda imid, env: QBIMIntersectionManager(
        imid, env, 30, 0.05, DistanceBasedUnit(imid, 75, lambda: env.intersections.get_position(imid))),
    "stip": None,
    "tl": lambda imid, env: TLIntersectionManager(imid, env, SINGLE_INTERSECTION_TL_PHASES)
}

vehicle_factory = {
    "qb_im": lambda vid, env: QBIMVehicle(vid, env,
                                          DistanceBasedUnit(vid, 75, lambda: env.vehicles.get_position(vid))),
    "stip": lambda vid, env: STIPVehicle(vid, env,
                                         DistanceBasedUnit(vid, 125, lambda: env.vehicles.get_position(vid))),
    "tl": lambda vid, env: TLVehicle(vid, env)
}


def main():
    logging.basicConfig(level=logging.DEBUG)
    algo = "stip"
    rate = 2.4999999999999996

    demand_generator = RandomDemandGenerator({
        "NE": rate, "NS": rate, "NW": rate,
        "EN": rate, "ES": rate, "EW": rate,
        "SN": rate, "SE": rate, "SW": rate,
        "WN": rate, "WE": rate, "WS": rate
    }, 0.05)
    # demand_generator = ConflictingDemandGenerator()
    net_config_file = "intersection_control/environments/sumo/networks/single_intersection/intersection.sumocfg"
    net_config_file = "/home/mario/Individual/IntersectionControl/intersection_control/environments/sumo/networks/single_intersection/intersection-mario.sumocfg"
    import sumolib
    parse_fast = iter(sumolib.xml.parse_fast(net_config_file, "net-file", "value"))
    print(iter(parse_fast))
    print(next(parse_fast))
    print("finished")
    exit()
    env = SumoEnvironment("./intersection_control/environments/sumo/networks/single_intersection/intersection-mario.sumocfg",
                          demand_generator=demand_generator, time_step=0.05, gui=True)

    intersection_managers = {im_factory[algo](intersection_id, env) for intersection_id in
                             env.intersections.get_ids()} if im_factory[algo] else None
    vehicles = {vehicle_factory[algo](vehicle_id, env) for vehicle_id in env.vehicles.get_ids()}

    for _ in range(STEP_COUNT):
        env.step()
        
        removed_vehicles = {v for v in vehicles if v.get_id() in env.get_removed_vehicles()}
        for v in removed_vehicles:
            v.destroy()
        new_vehicles = {vehicle_factory[algo](vehicle_id, env) for vehicle_id in env.get_added_vehicles()}
        vehicles = (vehicles - removed_vehicles).union(new_vehicles)
        
        for vehicle in vehicles:
            vehicle.step()
        if intersection_managers:
            for im in intersection_managers:
                im.step()

# this is the main entry point of this script
if __name__ == "__main__":
    import os
    import sys
    myDir = os.getcwd()
    sys.path.append(myDir)

    from pathlib import Path
    path = Path(myDir)
    a=str(path.parent.absolute())
    sys.path.append(a)

    main()