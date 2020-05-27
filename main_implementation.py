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
    """
    For a method of NDT approximation, this function samples random initial displacements 
    between given ranges and solves the Consensus and Naive NDT odometry.
    The time taken, rotation and displacement error of the Consensus and Naive NDT odometry 
    methdos is compared.
    """

    print('Setting model parameters')

    run_no = 7here
    plot_fig = True

    run_mode = 'server'
    #run_mode = 'laptop'
    total_iters = 20 # 20
    iter1 = 10 # 10
    iter2 = 10 # 10
    num_pcs = 30 #100
    num_odom_vects = 5 #10
    test_mode = 'overlap'  # 'nooverlap' 'interpolate'

    max_x = 0.4
    max_y = 0.4
    max_z = 0.1
    max_phi = 10
    max_theta = 10
    max_psi = 30

    odom_limits = np.array([max_x, max_y, max_z, max_phi, max_theta, max_psi])

    #scale_array = np.array([2., 1., 0.5])
    scale_array = np.array([2., 1.])
    #scale_array = np.array([1.])

    assert(total_iters == iter1 + iter2)

    print('Loading dataset')
    pcs = data_utils.load_uiuc_pcs(0, num_pcs-1, mode=run_mode)

    integrity_filters = np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    # integrity_filters = np.array([0.5, 0.8])
    num_int_vals = np.size(integrity_filters)

    print('Creating placeholder variables for storing errors')

    odom_vectors = np.zeros([num_int_vals, num_pcs, num_odom_vects, 6])

    vanilla_time = np.zeros([num_int_vals, num_pcs, num_odom_vects])
    vanilla_pos_error = np.zeros_like(vanilla_time)
    vanilla_rot_error = np.zeros_like(vanilla_time)

    consensus_time = np.zeros_like(vanilla_time)
    consensus_pos_error = np.zeros_like(vanilla_pos_error)
    consensus_rot_error = np.zeros_like(vanilla_rot_error)

    for pc_idx, ref_pc in enumerate(pcs):
        for odom_idx in range(num_odom_vects):

            rand_num = 2*(np.random.rand(6) - 0.5)
            test_odom = odom_limits*rand_num
            inv_test_odom = utils.invert_odom_transfer(test_odom)

            print('Creating transformed test point cloud')
            trans_pc = utils.transform_pc(test_odom, ref_pc)

            print('\nRunning vanilla multi-scale NDT for PC:', pc_idx, 'odometry: ', odom_idx, '\n')

            vanilla_odom, test_van_time, _ = ndt.multi_scale_ndt_odom(np.copy(ref_pc), np.copy(trans_pc), scale_array, 0.5,
                                                                   test_mode, total_iters, 0)
            #cv is going to be a dummy here

            for cv_idx, cv in enumerate(integrity_filters):
                print('\nExperiment for C_v:', cv, ' pc number:', pc_idx, 'odometry:', odom_idx, '\n')
                print('Running consensus multi-scale NDT')
                consensus_odom, test_con_time, _ = ndt.multi_scale_ndt_odom(np.copy(ref_pc), np.copy(trans_pc),
                                                                         scale_array, cv, test_mode, iter1, iter2)

                print('Computing and storing error and timing values')

                consensus_odom_diff = consensus_odom - inv_test_odom
                consensus_time[cv_idx, pc_idx, odom_idx] = test_con_time
                consensus_pos_error[cv_idx, pc_idx, odom_idx] = np.linalg.norm(consensus_odom_diff[:3])
                consensus_rot_error[cv_idx, pc_idx, odom_idx] = np.linalg.norm(consensus_odom_diff[3:])

            vanilla_odom_diff = vanilla_odom - inv_test_odom

            odom_vectors[:, pc_idx, odom_idx, :] = inv_test_odom

            vanilla_time[:, pc_idx, odom_idx] = test_van_time
            vanilla_pos_error[:, pc_idx, odom_idx] = np.linalg.norm(vanilla_odom_diff[:3])
            vanilla_rot_error[:, pc_idx, odom_idx] = np.linalg.norm(vanilla_odom_diff[3:])

        if pc_idx % 10 == 0:
            print('Saving computed values')
            np.save('consensus_values_' + test_mode + '_' + str(run_no), integrity_filters)
            np.save('odometry_vectors' + test_mode + '_' + str(run_no), odom_vectors)
            np.save("vanilla_time_" + test_mode + '_' + str(run_no), vanilla_time)
            np.save("vanilla_pos_error_" + test_mode + '_' + str(run_no), vanilla_pos_error)
            np.save("vanilla_rot_error_" + test_mode + '_' + str(run_no), vanilla_rot_error)

            np.save("consensus_time_" + test_mode + '_' + str(run_no), consensus_time)
            np.save("consensus_pos_error_" + test_mode + '_' + str(run_no), consensus_pos_error)
            np.save("consensus_rot_error_" + test_mode + '_' + str(run_no), consensus_rot_error)



    if plot_fig:
        plt.close('all')
        plot_vanilla_time = utils.plot_averaged(vanilla_time)
        plot_vanilla_pos_error = utils.plot_averaged(vanilla_pos_error)
        plot_vanilla_rot_error = utils.plot_averaged(vanilla_rot_error)

        plot_consensus_time = utils.plot_averaged(consensus_time)
        plot_consensus_pos_error = utils.plot_averaged(consensus_pos_error)
        plot_consensus_rot_error = utils.plot_averaged(consensus_rot_error)

        plt.figure()
        plt.plot(integrity_filters, plot_vanilla_time, label='Vanilla Timing')
        plt.plot(integrity_filters, plot_consensus_time, label='Consensus Timing')
        plt.title("Timing comparison")
        plt.legend(loc="upper right")

        plt.figure()
        plt.plot(integrity_filters, plot_vanilla_pos_error, label='Vanilla Position Error')
        plt.plot(integrity_filters, plot_consensus_pos_error, label='Consensus Position Error')
        plt.title("Position Error comparison")
        plt.legend(loc="upper right")

        plt.figure()
        plt.plot(integrity_filters, plot_vanilla_rot_error, label='Vanilla Rotation Error')
        plt.plot(integrity_filters, plot_consensus_rot_error, label='Consensus Rotation Error')
        plt.title('Rotation Error comparison')
        plt.legend(loc="upper right")

        plt.show()

    print('Saving computed values')
    np.save('consensus_values_' + test_mode + '_' + str(run_no), integrity_filters)
    np.save('odometry_vectors' + test_mode + '_' + str(run_no), odom_vectors)
    np.save("vanilla_time_" + test_mode + '_' + str(run_no), vanilla_time)
    np.save("vanilla_pos_error_" + test_mode + '_' + str(run_no), vanilla_pos_error)
    np.save("vanilla_rot_error_" + test_mode + '_' + str(run_no), vanilla_rot_error)

    np.save("consensus_time_" + test_mode + '_' + str(run_no), consensus_time)
    np.save("consensus_pos_error_" + test_mode + '_' + str(run_no), consensus_pos_error)
    np.save("consensus_rot_error_" + test_mode + '_' + str(run_no), consensus_rot_error)

    return 0


main()
