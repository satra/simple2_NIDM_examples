
import argparse
from os.path import join,basename,splitext,isfile
from os import system


def main():

    parser = argparse.ArgumentParser(prog='add_fsl_segvols.py',
                                     description='''This is essentially a helper script which takes a list of
                                     BIDS-formatted subject IDs with paths to the BIDS subject folders for abide
                                     and adhd200 datasets and downloads the Freesurfer-generated aseg.stats files
                                     from an Amazon S3 bucket and adds the brain volume data to existing NIDM-E files
                                     if the particular subject ID exists.  The NIDM-E files are expected to be
                                     in the site's directory in the BIDS dataset and called nidm.ttl (e.g. for
                                     ABIDE site SDSU: ./datasets.datalad.org/abide/RawDataBIDS/SDSU/nidm.ttl''',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-s','--subj',dest='subj',required=True, help='Text file containing 1 line per participant'
                                                                       'with relative paths to the location of the'
                                                                       'BIDS subject directory:'
                                                                       ''
                                                                       './datasets.datalad.org/abide/RawDataBIDS/SDSU/sub-0050197'
                                                                       './datasets.datalad.org/abide/RawDataBIDS/SDSU/sub-0050190'
                                                                       './datasets.datalad.org/abide/RawDataBIDS/SDSU/sub-0050199'
                                                                       '...')
    parser.add_argument('-new','--new', action='store_true', required=False, help="If flag set then new NIDM files will")

    args = parser.parse_args()

    with open(args.subj,'r') as f:
        for line in f:
            # set up command line for get brain volume data and adding it to existing NIDM file
            # first check if a NIDM file exists in the site location
            #strip training \n from line
            line=line.rstrip('\n')
            loc = line.find("sub")
            if not args.new:
                if not isfile(join(line[:loc-1],"nidm.ttl")):
                    print("No existing NIDM-E file for site: %s" %line[:loc-1])
                    print("Skipping subject: %s" %line[loc:])
                    continue
            # set up command to add brain volumes from Amazon bucket
            # https://fcp-indi.s3.amazonaws.com/data/Projects/ABIDE/Outputs/mindboggle_swf/simple_workflow/sub-0050665/segstats.json
            cmd="fslsegstats2nidm -f \"https://fcp-indi.s3.amazonaws.com/data/Projects/"
            #get dataset (abide or adhd200) from line
            if "abide" in line:
                cmd=cmd + "ABIDE/"
            elif "adhd200" in line:
                cmd=cmd + "ADHD200/"
            elif "corr" in line:
                cmd=cmd + "CORR/"
            else:
                print("Error, can't find dataset (abide | adhd200) in line: %s" %line)
                print("Skipping...")
                continue

            cmd=cmd + "Outputs/mindboggle_swf/simple_workflow/" + line[loc:] + \
                    "/segstats.json\" -subjid " + line[loc+4:]

            if not args.new:
                cmd = cmd + " -n " + line[:loc] + "nidm.ttl -o " + line[:loc] + \
                    "nidm.ttl"
            else:
                cmd = cmd + " -o " + join(line[:loc],"nidm.ttl")

            # execute command
            print(cmd)
            system(cmd)


if __name__ == "__main__":
    main()
