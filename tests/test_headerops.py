# -*- coding: utf-8 -*-
from pairsamtools import _headerops

from nose.tools import assert_raises, with_setup, raises

def test_make_standard_header():
    header = _headerops.make_standard_pairsheader()

    assert any([l.startswith('## pairs format') for l in header])
    assert any([l.startswith('#shape') for l in header])
    assert any([l.startswith('#columns') for l in header])

    header = _headerops.make_standard_pairsheader(chromosomes=['b', 'c', 'a'])

    assert any([l.startswith('#chromosomes') for l in header])

def test_samheaderops():
    header = _headerops.make_standard_pairsheader()
    samheader = [
        '@SQ\tSN:chr1\tLN:100',
        '@SQ\tSN:chr2\tLN:100',
        '@SQ\tSN:chr3\tLN:100',
        '@PG\tID:bwa\tPN:bwa\tCL:bwa',
        '@PG\tID:bwa-2\tPN:bwa\tCL:bwa\tPP:bwa'
    ]
    header_with_sam = _headerops.insert_samheader(header, samheader)
    
    assert len(header_with_sam) == len(header) + len(samheader)
    for l in samheader:
        assert any([l2.startswith('#samheader') and l in l2 
                    for l2 in header_with_sam])

    # test adding new programs to the PG chain
    header_extra_pg = _headerops.append_new_pg(
        header_with_sam, ID='test', PN='test')

    # test if all lines got transferred
    assert all([(old_l in header_extra_pg) for old_l in header_with_sam])
    # test if one PG got added
    assert len(header_extra_pg) == len(header_with_sam) + 1

    # test if the new PG has PP matching the ID of one of already existing PGs
    new_l = [l for l in header_extra_pg if l not in header_with_sam][0]
    pp = [f[3:] for f in new_l.split('\t') if f.startswith('PP:')][0]
    assert len([l for l in header_extra_pg
                if l.startswith('#samheader') 
                    and ('\tID:{}\t'.format(pp) in l)
                ]) == 1


def test_merge_pairheaders():
    headers = [
        ['## pairs format v1.0'],
        ['## pairs format v1.0']
    ]
    merged_header = _headerops._merge_pairheaders(headers)
    assert merged_header == headers[0]

    headers = [
        ['## pairs format v1.0',
         '#a'],
        ['## pairs format v1.0',
         '#b']
    ]
    merged_header = _headerops._merge_pairheaders(headers)
    assert merged_header == ['## pairs format v1.0',
                             '#a',
                             '#b']

    headers = [
        ['## pairs format v1.0',
         '#chromosomes: chr1 chr2'],
        ['## pairs format v1.0',
         '#chromosomes: chr1 chr2'],
    ]
    merged_header = _headerops._merge_pairheaders(headers)
    assert merged_header == headers[0]

@raises(Exception)
def test_merge_different_pairheaders():
    headers = [
        ['## pairs format v1.0'],
        ['## pairs format v1.1']
    ]
    merged_header = _headerops._merge_pairheaders(headers)

def test_force_merge_pairheaders():
    headers = [
        ['## pairs format v1.0',
         '#chromosomes: chr1'],
        ['## pairs format v1.0',
         '#chromosomes: chr2'],
    ]
    merged_header = _headerops._merge_pairheaders(headers, force=True)
    assert merged_header == ['## pairs format v1.0',
                             '#chromosomes: chr1 chr2']

def test_merge_samheaders():
    headers = [
        ['@HD\tVN:1'],
        ['@HD\tVN:1'],
    ]
    merged_header = _headerops._merge_samheaders(headers)
    assert merged_header == headers[0]

    headers = [
        ['@HD\tVN:1',
         '@SQ\tSN:chr1\tLN:100',
         '@SQ\tSN:chr2\tLN:100',
        ],
        ['@HD\tVN:1',
         '@SQ\tSN:chr1\tLN:100',
         '@SQ\tSN:chr2\tLN:100',
        ],
    ]
    merged_header = _headerops._merge_samheaders(headers)
    assert merged_header == headers[0]

    headers = [
        ['@HD\tVN:1',
         '@PG\tID:bwa\tPN:bwa\tPP:cat',
        ],
        ['@HD\tVN:1',
         '@PG\tID:bwa\tPN:bwa\tPP:cat',
        ],
    ]
    merged_header = _headerops._merge_samheaders(headers)
    print(merged_header)
    assert merged_header == [
        '@HD\tVN:1',
        '@PG\tID:bwa-1\tPN:bwa\tPP:cat-1',
        '@PG\tID:bwa-2\tPN:bwa\tPP:cat-2',
        ]

def test_merge_headers():
    headers = [
        ['## pairs format v1.0',
         '#chromosomes: chr1 chr2',
         '#samheader: @HD\tVN:1',
         '#samheader: @SQ\tSN:chr1\tLN:100',
         '#samheader: @SQ\tSN:chr2\tLN:100']
    ] * 2

    merged_header = _headerops.merge_headers(headers)
    assert merged_header == headers[0]
