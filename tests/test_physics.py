#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# @file   test_physics.py
# @author Albert Puig (albert.puig@cern.ch)
# @date   27.02.2019
# =============================================================================
"""Test physics output."""

import os
import platform

import numpy as np
from scipy.stats import ks_2samp

if platform.system() == 'Darwin':
    import matplotlib
    matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import uproot

import tensorflow as tf

from tfphasespace import tfphasespace


BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REF_FILE = os.path.join(BASE_PATH, 'data', 'bto3pi.root')
PLOT_DIR = os.path.join(BASE_PATH, 'tests', 'plots')

B_MASS = 5279.0
B_AT_REST = tf.stack((0.0, 0.0, 0.0, B_MASS), axis=-1)
PION_MASS = 139.6


def create_ref_histos(n_pions):
    """Load reference histogram data."""
    def make_histos(vector_list, range_, weights=None):
        """Make histograms."""
        v_array = np.stack([vector_list.x, vector_list.y, vector_list.z, vector_list.E])
        histos = tuple(np.histogram(v_array[coord], 100, range=range_, weights=weights)[0]
                       for coord in range(4))
        return tuple(histo/np.sum(histo) for histo in histos)

    ref_file = os.path.join(BASE_PATH, 'data', 'bto{}pi.root'.format(n_pions))
    if not os.path.exists(ref_file):
        script = os.path.join(BASE_PATH,
                              'scripts',
                              'prepare_test_samples.cxx+({})'.format(','.join(
                                  '"{}"'.format(os.path.join(BASE_PATH,
                                                             'data',
                                                             'bto{}pi.root'.format(i+1))
                                                for i in range(4)))))
        os.system("root -qb '{}'".format(script))
    events = uproot.open(ref_file)['events']
    pion_names = ['pion_{}'.format(pion+1) for pion in range(n_pions)]
    pions = {pion_name: events.array(pion_name)
             for pion_name in pion_names}
    weights = events.array('weight')
    weights_histo = np.histogram(weights, 100, range=(0, 1))[0]
    return sum([make_histos(pion, range_=(-3000, 3000), weights=weights)
                for pion in pions.values()], tuple()), \
        weights_histo/np.sum(weights_histo)


def make_norm_histo(array, range_, weights=None):
    """Make histo and modify dimensions."""
    histo = np.histogram(array, 100, range=range_, weights=weights)[0]
    return histo/np.sum(histo)


def test_two_body():
    """Test B->pipi decay."""
    weights, particles = tf.Session().run(tfphasespace.generate(B_AT_REST,
                                                                [PION_MASS, PION_MASS],
                                                                100000))
    parts = np.concatenate(particles, axis=0)
    histos = [make_norm_histo(parts[coord],
                              range_=(-3000, 3000),
                              weights=weights)
              for coord in range(parts.shape[0])]
    weight_histos = make_norm_histo(weights, range_=(0, 1))
    ref_histos, ref_weights = create_ref_histos(2)
    p_values = np.array([ks_2samp(histos[coord], ref_histos[coord])[1]
                         for coord, _ in enumerate(histos)] +
                        [ks_2samp(weight_histos, ref_weights)[1]])
    # Let's plot
    x = np.linspace(-3000, 3000, 100)
    if not os.path.exists(PLOT_DIR):
        os.mkdir(PLOT_DIR)
    for coord, _ in enumerate(histos):
        plt.hist(x, weights=histos[coord], alpha=0.5, label='tfphasespace', bins=100)
        plt.hist(x, weights=ref_histos[coord], alpha=0.5, label='TGenPhasespace', bins=100)
        plt.legend(loc='upper right')
        plt.savefig(os.path.join(PLOT_DIR,
                                 "two_body_pion_{}_{}.png".format(int(coord / 4) + 1,
                                                                  ['x', 'y', 'z', 'e'][coord % 4])))
        plt.clf()
    plt.hist(np.linspace(0, 1, 100), weights=weight_histos, alpha=0.5, label='tfphasespace', bins=100)
    plt.hist(np.linspace(0, 1, 100), weights=ref_weights, alpha=0.5, label='tfphasespace', bins=100)
    assert np.all(p_values > 0.05)


def test_three_body():
    """Test B -> pi pi pi decay."""
    weights, particles = tf.Session().run(tfphasespace.generate(B_AT_REST,
                                                                [PION_MASS, PION_MASS, PION_MASS],
                                                                100000))
    parts = np.concatenate(particles, axis=0)
    histos = [make_norm_histo(parts[coord],
                              range_=(-3000, 3000),
                              weights=weights)
              for coord in range(parts.shape[0])]
    weight_histos = make_norm_histo(weights, range_=(0, 1))
    ref_histos, ref_weights = create_ref_histos(3)
    p_values = np.array([ks_2samp(histos[coord], ref_histos[coord])[1]
                         for coord, _ in enumerate(histos)] +
                        [ks_2samp(weight_histos, ref_weights)[1]])
    # Let's plot
    x = np.linspace(-3000, 3000, 100)
    if not os.path.exists(PLOT_DIR):
        os.mkdir(PLOT_DIR)
    for coord, _ in enumerate(histos):
        plt.hist(x, weights=histos[coord], alpha=0.5, label='tfphasespace', bins=100)
        plt.hist(x, weights=ref_histos[coord], alpha=0.5, label='TGenPhasespace', bins=100)
        plt.legend(loc='upper right')
        plt.savefig(os.path.join(PLOT_DIR,
                                 "three_body_pion_{}_{}.png".format(int(coord / 4) + 1,
                                                                    ['x', 'y', 'z', 'e'][coord % 4])))
        plt.clf()
    plt.hist(np.linspace(0, 1, 100), weights=weight_histos, alpha=0.5, label='tfphasespace', bins=100)
    plt.hist(np.linspace(0, 1, 100), weights=ref_weights, alpha=0.5, label='tfphasespace', bins=100)
    plt.savefig(os.path.join(PLOT_DIR, 'three_body_weights.png'))
    plt.clf()
    assert np.all(p_values > 0.05)


def test_four_body():
    """Test B -> pi pi pi pi decay."""
    weights, particles = tf.Session().run(tfphasespace.generate(B_AT_REST,
                                                                [PION_MASS, PION_MASS, PION_MASS, PION_MASS],
                                                                100000))
    parts = np.concatenate(particles, axis=0)
    histos = [make_norm_histo(parts[coord],
                              range_=(-3000, 3000),
                              weights=weights)
              for coord in range(parts.shape[0])]
    weight_histos = make_norm_histo(weights, range_=(0, 1))
    ref_histos, ref_weights = create_ref_histos(4)
    p_values = np.array([ks_2samp(histos[coord], ref_histos[coord])[1]
                         for coord, _ in enumerate(histos)] +
                        [ks_2samp(weight_histos, ref_weights)[1]])
    # Let's plot
    x = np.linspace(-3000, 3000, 100)
    if not os.path.exists(PLOT_DIR):
        os.mkdir(PLOT_DIR)
    for coord, _ in enumerate(histos):
        plt.hist(x, weights=histos[coord], alpha=0.5, label='tfphasespace', bins=100)
        plt.hist(x, weights=ref_histos[coord], alpha=0.5, label='TGenPhasespace', bins=100)
        plt.legend(loc='upper right')
        plt.savefig(os.path.join(PLOT_DIR,
                                 "four_body_pion_{}_{}.png".format(int(coord / 4) + 1,
                                                                   ['x', 'y', 'z', 'e'][coord % 4])))
        plt.clf()
    plt.hist(np.linspace(0, 1, 100), weights=weight_histos, alpha=0.5, label='tfphasespace', bins=100)
    plt.hist(np.linspace(0, 1, 100), weights=ref_weights, alpha=0.5, label='tfphasespace', bins=100)
    plt.savefig(os.path.join(PLOT_DIR, 'four_body_weights.png'))
    plt.clf()
    assert np.all(p_values > 0.05)


if __name__ == "__main__":
    test_two_body()
    test_three_body()
    test_four_body()


# EOF
