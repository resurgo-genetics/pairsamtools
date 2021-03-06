#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
import click
import subprocess

from . import _common, cli, _headerops

UTIL_NAME = 'pairsam_sort'

@cli.command()

@click.argument(
    'pairsam_path', 
    type=str,
    required=False)

@click.option(
    '-o', "--output", 
    type=str, 
    default="", 
    help='output pairsam file.'
        ' If the path ends with .gz, the output is bgzip-compressed.'
        ' By default, the output is printed into stdout.')

@click.option(
    "--nproc", 
    type=int, 
    default=8, 
    show_default=True,
    help='Number of processes to split the work between.'
    )

@click.option(
    "--tmpdir", 
    type=str, 
    default='', 
    help='Custom temporary folder for sorting intermediates.'
    )

@click.option(
    "--memory", 
    type=str, 
    default='2G', 
    show_default=True,
    help='The amount of memory used by default.',

    )


def sort(pairsam_path, output, nproc, tmpdir, memory):
    '''sort a pairs/pairsam file. 
    
    The resulting order is lexicographic along chrom1 and chrom2, numeric 
    along pos1 and pos2 and lexicographic along pair_type.

    PAIRSAM_PATH : input .pairsam file. If the path ends with .gz, the input is
    gzip-decompressed. By default, the input is read from stdin.
    '''

    instream = (_common.open_bgzip(pairsam_path, mode='r', nproc=nproc) 
                if pairsam_path else sys.stdin)
    outstream = (_common.open_bgzip(output, mode='w', nproc=nproc) 
                 if output else sys.stdout)

    header, body_stream = _headerops.get_header(instream)
    header = _headerops.append_new_pg(header, ID=UTIL_NAME, PN=UTIL_NAME)
    header = _headerops.mark_header_as_sorted(header)

    outstream.writelines((l+'\n' for l in header))

    outstream.flush()

    command = r'''
        /bin/bash -c 'export LC_COLLATE=C; export LANG=C; sort 
        -k {0},{0} -k {1},{1} -k {2},{2}n -k {3},{3}n -k {4},{4} 
        --stable
        --field-separator=$'\''{5}'\'' 
        {6}
        {7}
        -S {8}
        '''.replace('\n',' ').format(
                _common.COL_C1+1, 
                _common.COL_C2+1, 
                _common.COL_P1+1, 
                _common.COL_P2+1,
                _common.COL_PTYPE+1,
                _common.PAIRSAM_SEP_ESCAPE,
                ' --parallel={} '.format(nproc) if nproc > 1 else ' ',
                ' -T {} '.format(tmpdir) if tmpdir else ' ',
                memory
        )
    command += "'"

    with subprocess.Popen(
            command, stdin=subprocess.PIPE, bufsize=-1, shell=True,
            stdout=outstream) as process:
        stdin_wrapper = io.TextIOWrapper(process.stdin, 'utf-8')
        for line in body_stream:
            stdin_wrapper.write(line)
        stdin_wrapper.flush()
        process.communicate()

    if instream != sys.stdin:
        instream.close()

    if outstream != sys.stdout:
        outstream.close()


if __name__ == '__main__':
    sort()
