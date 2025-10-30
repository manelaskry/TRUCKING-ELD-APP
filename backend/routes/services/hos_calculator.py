from typing import List, Dict
from datetime import timedelta


class HOSCalculator:

   
    MAX_DRIVING_TIME = 11        
    MAX_ON_DUTY_TIME = 14        
    REQUIRED_BREAK_AFTER = 8     
    BREAK_DURATION = 0.5
    REST_PERIOD = 10             
    CYCLE_LIMIT = 70            

    def __init__(self, current_cycle_used: float):
        self.current_cycle_used = current_cycle_used
        self.available_hours = self.CYCLE_LIMIT - current_cycle_used

    def calculate_trip_schedule(
        self,
        total_distance: float,
        total_duration: float,
        fuel_stops: List[float]
    ) -> List[Dict]:
        
        schedule = []
        current_time = 0.0  
        current_driving_time = 0.0
        current_on_duty_time = 0.0
        distance_covered = 0.0

        avg_speed = total_distance / total_duration if total_duration > 0 else 55

        
        schedule.append({
            'type': 'pickup',
            'start_time': current_time,
            'duration': 1,
            'status': 'on_duty',
            'distance': 0
        })
        current_time += 1
        current_on_duty_time += 1

        
        while distance_covered < total_distance:
            
            if current_driving_time >= self.REQUIRED_BREAK_AFTER:
                schedule.append({
                    'type': 'break',
                    'start_time': current_time,
                    'duration': self.BREAK_DURATION,
                    'status': 'off_duty',
                    'distance': distance_covered
                })
                current_time += self.BREAK_DURATION
                current_driving_time = 0

            if current_on_duty_time >= self.MAX_ON_DUTY_TIME:
                schedule.append({
                    'type': 'rest',
                    'start_time': current_time,
                    'duration': self.REST_PERIOD,
                    'status': 'sleeper',
                    'distance': distance_covered
                })
                current_time += self.REST_PERIOD
                current_driving_time = 0
                current_on_duty_time = 0

            next_fuel_stop = next((f for f in fuel_stops if distance_covered < f <= distance_covered + 100), None)

            if next_fuel_stop:
                distance_to_fuel = next_fuel_stop - distance_covered
                drive_time = distance_to_fuel / avg_speed

                schedule.append({
                    'type': 'driving',
                    'start_time': current_time,
                    'duration': drive_time,
                    'status': 'driving',
                    'distance': distance_covered,
                    'distance_end': next_fuel_stop
                })

                current_time += drive_time
                current_driving_time += drive_time
                current_on_duty_time += drive_time
                distance_covered = next_fuel_stop

                schedule.append({
                    'type': 'fuel',
                    'start_time': current_time,
                    'duration': 0.5,
                    'status': 'on_duty',
                    'distance': distance_covered
                })
                current_time += 0.5
                current_on_duty_time += 0.5
            else:
                remaining_distance = total_distance - distance_covered
                time_until_break = self.REQUIRED_BREAK_AFTER - current_driving_time
                time_until_rest = self.MAX_ON_DUTY_TIME - current_on_duty_time

                max_drive_time = min(
                    time_until_break,
                    time_until_rest,
                    self.MAX_DRIVING_TIME - current_driving_time,
                    remaining_distance / avg_speed
                )

                if max_drive_time <= 0:
                    break  

                drive_distance = max_drive_time * avg_speed

                schedule.append({
                    'type': 'driving',
                    'start_time': current_time,
                    'duration': max_drive_time,
                    'status': 'driving',
                    'distance': distance_covered,
                    'distance_end': distance_covered + drive_distance
                })

                current_time += max_drive_time
                current_driving_time += max_drive_time
                current_on_duty_time += max_drive_time
                distance_covered += drive_distance

        schedule.append({
            'type': 'dropoff',
            'start_time': current_time,
            'duration': 1,
            'status': 'on_duty',
            'distance': total_distance
        })

        return schedule
