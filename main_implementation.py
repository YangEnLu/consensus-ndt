"""
main_implementation.py
File for the offline implementation of NDT-SLAM on the NAVLab resident powerhouse machine
Author: Ashwin Kanhere
Date Created: 16th June 2019
Date Modified: 2nd February, 2020
"""
import numpy as np
import ndt
import utils
from matplotlib import pyplot as plt
import data_utils


def main():

    print('Setting model parameters')

    run_no = 1
    plot_fig = True

    #run_mode = 'server'
    run_mode = 'laptop'
    total_iters = 20
    iter1 = 10
    iter2 = 10
    num_pcs = 5 #100
    num_odom_vects = 2 #10
    test_mode = 'overlapping'  # 'nooverlap' 'interpolate'

    max_x = 0.4
    max_y = 0.4
    max_z = 0.1
    max_phi = 10
    max_theta = 10
    max_psi = 30

    odom_limits = np.array([max_x, max_y, max_z, max_phi, max_theta, max_psi])

    scale_array = np.array([2., 1., 0.5])

    assert(total_iters == iter1 + iter2)

    print('Loading dataset')
    pcs = data_utils.load_uiuc_pcs(0, num_pcs, mode=run_mode)

    integrity_filters = np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    num_int_vals = np.size(integrity_filters)

    print('Creating placeholder variables for storing errors')

    vanilla_time = np.zeros([num_int_vals, num_pcs, num_odom_vects])
    vanilla_pos_error = np.zeros_like(vanilla_time)
    vanilla_rot_error = np.zeros_like(vanilla_time)

    consensus_time = np.zeros_like(vanilla_time)
    consensus_pos_error = np.zeros_like(vanilla_pos_error)
    consensus_rot_error = np.zeros_like(vanilla_rot_error)

    for pc_idx, ref_pc in enumerate(pcs):
        for odom_idx in range(num_int_vals):

            rand_num = 2*(np.random.rand(6) - 0.5)
            test_odom = odom_limits*rand_num
            inv_test_odom = utils.invert_odom_transfer(test_odom)

            print('Creating transformed test point cloud')
            trans_pc = utils.transform_pc(test_odom, ref_pc)

            print('Running vanilla multi-scale NDT')
            vanilla_odom, test_van_time = ndt.multi_scale_ndt_odom(np.copy(ref_pc), np.copy(trans_pc), scale_array, 0.5,
                                                                   test_mode, total_iters, 0)
            #cv is going to be a dummy here

            for cv_idx, cv in enumerate(integrity_filters):
                print('Experiment for C_v:', cv, ' pc number:', pc_idx, 'odometry:', odom_idx)
                print('Running consensus multi-scale NDT')
                consensus_odom, test_con_time = ndt.multi_scale_ndt_odom(np.copy(ref_pc), np.copy(trans_pc),
                                                                         scale_array, cv, test_mode, iter1, iter2)

                print('Computing and storing error and timing values')

                vanilla_odom_diff = vanilla_odom - inv_test_odom
                vanilla_time[:, pc_idx, odom_idx] = test_van_time
                vanilla_pos_error[:, pc_idx, odom_idx] = np.linalg.norm(vanilla_odom_diff[:3])
                vanilla_rot_error[:, pc_idx, odom_idx] = np.linalg.norm(vanilla_odom_diff[3:])

                consensus_odom_diff = consensus_odom - inv_test_odom
                consensus_time[cv_idx, pc_idx, odom_idx] = test_con_time
                consensus_pos_error[cv_idx, pc_idx, odom_idx] = np.linalg.norm(consensus_odom_diff[:3])
                consensus_rot_error[cv_idx, pc_idx, odom_idx] = np.linalg.norm(consensus_odom_diff[3:])

    print('Saving computed values')
    np.save("vanilla_time" + test_mode + str(run_no), vanilla_time)
    np.save("vanilla_pos_error" + test_mode + str(run_no), vanilla_pos_error)
    np.save("vanilla_rot_error" + test_mode + str(run_no), vanilla_rot_error)

    np.save("consensus_time" + test_mode + str(run_no), consensus_time)
    np.save("consensus_time" + test_mode + str(run_no), consensus_pos_error)
    np.save("consensus_time" + test_mode + str(run_no), consensus_rot_error)

    if plot_fig:
        # TODO: Check this particular line of code and make sure it's taking the right mean
        plot_vanilla_time = np.mean(vanilla_time, axis=0)
        plot_vanilla_pos_error = np.mean(vanilla_pos_error, axis=0)
        plot_vanilla_rot_error = np.mean(vanilla_rot_error, axis=0)

        plot_consensus_time = np.mean(consensus_time, axis=0)
        plot_consensus_pos_error = np.mean(consensus_pos_error, axis=0)
        plot_consensus_rot_error = np.mean(consensus_rot_error, axis=0)

        plt.figure(1)
        plt.plot(integrity_filters, plot_vanilla_time, label='vanilla')
        plt.plot(integrity_filters, plot_consensus_time, label='consensus')
        plt.title("Timing comparison")
        plt.legend(loc="upper left")

        plt.figure(2)
        plt.plot(integrity_filters, plot_vanilla_pos_error, label='vanilla')
        plt.plot(integrity_filters, plot_consensus_pos_error, label='consensus')
        plt.title('Position error comparison')
        plt.legend(loc="upper left")

        plt.figure(3)
        plt.plot(integrity_filters, plot_vanilla_rot_error, label='vanilla')
        plt.plot(integrity_filters, plot_consensus_rot_error, label='consensus')
        plt.title('Rotation error comparison')
        plt.legend(loc="upper left")

        plt.show()

    return 0


main()
