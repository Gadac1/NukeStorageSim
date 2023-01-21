from solver import *
from load_interpolation import *
from class_definition import *
import numpy as np
import matplotlib.pyplot as plt    
import inquirer
from matplotlib.ticker import StrMethodFormatter



def run(PN_reac, storage_time, profile):

    (reac, hot_tank, cold_tank, max_stored_energy, P_unload_max)  = system_initialize(PN_reac, storage_time)
    P_grid = np.array(profile)*(system_max_power/eta)/100
    (Time, P_core, P_load, P_unload, stored_energy) = load_following(P_grid, reac, max_stored_energy, P_unload_max)

    print('')
    print('Case study :')
    print('     Reactor nominal power: ' + str(PN_reac) + 'MWe')
    print('     Storage system power: ' + str(system_max_power - PN_reac) + 'MWe')
    print('     Nominal storage time: ' + str(storage_time) + 'h')
    print('')
    print('Results :')
    print('     Storage capacity: ' + str(int(Joules_to_MWh(max_stored_energy))) + 'MWh')
    print('     Mass of nitrate salt: ' + str(int(hot_tank.V_max*nitrate_salt.rho/1000)) + 't')
    print('     Load factor of reactor with storage: ' + str(load_factor(P_core, reac)) + '%')
    print('     Consumption-Production equilibrium: ' + str(grid_equilibrium(P_grid, P_core, P_unload)))
    print('')

    print_load_graph(P_grid, reac, max_stored_energy, Time, P_core, P_load, P_unload, stored_energy, 0, len(P_grid)-1)

def min_storage_time(PN_reac, profile): # Computes minimum storage capacity in hours to mach the grid
    c = 0
    eq = False
    while eq == False: 
        c+=0.5
        (reac, hot_tank, cold_tank, max_stored_energy, P_unload_max)  = system_initialize(PN_reac, c)
        P_grid = np.array(profile)*(system_max_power/eta)/100
        (Time, P_core, P_load, P_unload, stored_energy) = load_following(P_grid, reac, max_stored_energy, P_unload_max)
        eq = grid_equilibrium(P_grid, P_core, P_unload)
    
    kp = load_factor(P_core, reac)
    m_salt = int(hot_tank.V_max*nitrate_salt.rho/1000)

    return c, kp, m_salt

def storage_time_study(profile):
    capacity = []
    nominal_power = []
    kp = []
    salt_mass = []

    for P in range(25,500,25):
        print('Studying ' + str(P) + 'MW reactor...')
        (c,k,mass) = min_storage_time(P, profile)
        capacity.append(c)
        kp.append(k)
        salt_mass.append(mass)
        nominal_power.append(P)

    print('')
    print('Done !')
    print('Displaying results...')

    fig = plt.figure()
    gs = gridspec.GridSpec(2,2)

    ax1=fig.add_subplot(gs[0,0])
    ax1.plot(nominal_power,capacity, 'k.', label = 'Storage capacity in hours')
    ax1.set_title('Minimum storage capacity in hours to match grid requirements')
    plt.ylabel('Storage capacity (h)')
    plt.xlabel('Reactor nominal power')
    ax1.set_xticks(np.arange(0, max(nominal_power), 50))
    ax1.set_yticks(np.arange(0, max(capacity), 5))
    ax1.grid(which='major', color='#DDDDDD', linewidth=1)
    ax1.grid()
    ax1.grid(which='minor', color='#EEEEEE', linestyle='--', linewidth=0.75)
    ax1.minorticks_on()
    ax1.grid()


    ax2=fig.add_subplot(gs[0,1])
    ax2.plot(nominal_power,salt_mass, 'k.', label = 'Storage capacity in salt mass')
    ax2.set_title('Minimum storage capacity in salt mass to match grid requirements')
    ax2.yaxis.set_major_formatter(StrMethodFormatter('{x:,}'))
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position("right")
    ax2.set_xticks(np.arange(0, max(nominal_power), 50))
    ax2.set_yticks(np.arange(0, max(salt_mass), 50000))
    plt.ylabel('Salt mass (t)')
    plt.xlabel('Reactor nominal power')
    ax2.grid(which='major', color='#DDDDDD', linewidth=1)
    ax2.grid()
    ax2.grid(which='minor', color='#EEEEEE', linestyle='--', linewidth=0.75)
    ax2.minorticks_on()
    ax2.grid()

    ax3=fig.add_subplot(gs[1,:])
    ax3.plot(nominal_power, kp, 'k.', label = 'Capacity factor at minimal storage requirements')
    ax3.set_title('Capacity factor at minimal storage requirement')
    ax3.yaxis.set_major_formatter(StrMethodFormatter('{x:,}'))
    ax3.set_xticks(np.arange(0, max(nominal_power), 50))
    ax3.set_yticks(np.arange(0, 105, 5))
    plt.ylabel('Capacity factor (%)')
    plt.xlabel('Reactor nominal power')
    ax3.grid(which='major', color='#DDDDDD', linewidth=1)
    ax3.grid()
    ax3.grid(which='minor', color='#EEEEEE', linestyle='--', linewidth=0.75)
    ax3.minorticks_on()
    ax3.grid()
    plt.show()

def interface():
    print('')
    questions = [
    inquirer.List('Penetration rate',
                    message="Input VRE penetration rate: ",
                    choices=['50', '80', '90'],),]
    answers = inquirer.prompt(questions)
    rate = int(answers["Penetration rate"])
    print('')
    questions = [
    inquirer.List('Season',
                    message="Input season: ",
                    choices=['Winter', 'Summer'],),]
    answers = inquirer.prompt(questions)
    season = str(answers["Season"])
    print('')

    if season == 'Winter':
        if rate == 50:
            profile = profil_50EnR_sem_winter
        elif rate == 80:
            profile = profil_80EnR_sem_winter
        else:
            profile = profil_90EnR_sem_winter
    else:
        if rate == 50:
            profile = profil_50EnR_sem_sum
        elif rate == 80:
            profile = profil_80EnR_sem_sum
        else:
            profile = profil_90EnR_sem_sum

    questions = [
    inquirer.List('Study',
                    message="Do you wish to simulate a specific system or perform a parametric study ?",
                    choices=['Specific system', 'Parametric study'],),]
    answers = inquirer.prompt(questions)

    if answers["Study"] == 'Specific system':
        print('')
        print('Input reactor nominal power in MWe: ')
        np = int(input())
        print('')
        print('Input storage duration: ')
        storage = float(input())
        run(np, storage, profile)
    else:
        storage_time_study(profile)

interface()
