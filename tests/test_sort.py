# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import click
from nose.tools import assert_raises



testdir = os.path.dirname(os.path.realpath(__file__))

def test_mock_pairsam():
    mock_pairsam_path = os.path.join(testdir, 'data', 'mock.pairsam')
    result = subprocess.check_output(
        ['python',
         '../utils/pairsam_sort.py',
         '--input',
         mock_pairsam_path],
        ).decode('ascii')

    # check if the header got transferred correctly
    pairsam_header = [l.strip() for l in open(mock_pairsam_path, 'r') if l.startswith('#')]
    output_header  = [l.strip() for l in result.split('\n') if l.startswith('#')] 
    for l in pairsam_header:
        assert any([l in l2 for l2 in pairsam_header])
        
    # Check that the only modified string is a @PG record of a SAM header
    for l in output_header:
        if not any([l in l2 for l2 in output_header]):
            assert l.startswith('#@PG')

    pairsam_body = [l.strip() for l in open(mock_pairsam_path, 'r') 
                    if not l.startswith('#') and l.strip()]
    output_body  = [l.strip() for l in result.split('\n')
                    if not l.startswith('#') and l.strip()]

    # check that all pairsam entries survived sorting:
    print(pairsam_body)
    print(output_body)
    assert len(pairsam_body) == len(output_body)

    # check the sorting order of the output:
    prev_pair = None
    for l in output_body:
        cur_pair = l.split('\v')[1:8]
        if prev_pair is not None:
            assert (cur_pair[0] >= prev_pair[0])
            if (cur_pair[0] == prev_pair[0]):
                assert (cur_pair[1] >= prev_pair[1])
                if (cur_pair[1] == prev_pair[1]):
                    assert (cur_pair[2] >= prev_pair[2]) 
                    if (cur_pair[2] == prev_pair[2]):
                        assert (cur_pair[3] >= prev_pair[3])

        prev_pair = cur_pair

