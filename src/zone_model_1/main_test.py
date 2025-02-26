if __name__ == "__main__":
    from zone_model_1 import main_model_as_function
    import pandas as pd

    (
        output_time_arr,
        output_gas_temp_arr,
        output_char_depth_arr,
        output_charring_rate_arr,
        output_MLR_arr,
        output_HRR_wood_arr,
        output_HRR_total_arr,
        output_HRR_ext_arr,
        HRR_time_arr,
        HRR_hrr_arr,
    ) = main_model_as_function()

    import matplotlib.pyplot as plt

    # Convert HRR arrays to kW
    HRR_hrr_arr = [x / 1000 for x in HRR_hrr_arr]
    output_HRR_wood_arr = [x / 1000 for x in output_HRR_wood_arr]
    output_HRR_total_arr = [x / 1000 for x in output_HRR_total_arr]
    output_HRR_ext_arr = [x / 1000 for x in output_HRR_ext_arr]

    # Generate new array for Total HRR
    combined_HRR =[]
    for i in range(len(output_HRR_total_arr)):
        combined_HRR.append(output_HRR_total_arr[i] + output_HRR_ext_arr[i])

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax1 = plt.subplots()
    ax1.plot(output_time_arr, output_gas_temp_arr, label='Gas')
    ax1.set_ylabel('Temperature [$^o$C]')
    ax1.minorticks_on()
    fig.tight_layout()

    fig, ax2 = plt.subplots()
    ax2.plot(output_time_arr, output_char_depth_arr, label='Char')
    ax2.set_xlabel('Time [min]')
    ax2.set_ylabel('Char depth [mm]')
    fig.tight_layout()

    fig, ax3 = plt.subplots()
    ax3.plot(output_time_arr, output_charring_rate_arr, label='Char')
    ax3.set_xlabel('Time [min]')
    ax3.set_ylabel('Charring rate [mm/min]')
    fig.tight_layout()

    fig, ax4 = plt.subplots()
    ax4.plot(output_time_arr, output_MLR_arr, label='Char')
    ax4.set_xlabel('Time [min]')
    ax4.set_ylabel('MLR [kg/m$^2$/s]')
    fig.tight_layout()

    fig, ax5 = plt.subplots()
    ax5.plot(output_time_arr, output_HRR_wood_arr, label='wood')
    ax5.plot(HRR_time_arr, HRR_hrr_arr, label='contents')
    ax5.plot(output_time_arr, output_HRR_total_arr, label='total internal')
    ax5.plot(output_time_arr, output_HRR_ext_arr, label='total external')
    ax5.plot(output_time_arr, combined_HRR, label='total combined')
    ax5.set_xlabel('Time [min]')
    ax5.set_ylabel('HRR [kW]')
    ax5.legend().set_visible(True)
    fig.tight_layout()

    plt.show()

    # Write columns to dataframe for exporting to .csv

    df = pd.DataFrame(output_time_arr, columns=['Output time [min]'])

    df['Output HRR from wood [kW]'] = output_HRR_wood_arr
    df['Output HRR inside enclosure [kW]'] = output_HRR_total_arr
    df['Output HRR external to enclosure [kW]'] = output_HRR_ext_arr
    df['Output HRR total [kW]'] = combined_HRR
    df.to_csv('zone_model_out.csv', encoding='utf-8', index=False)

