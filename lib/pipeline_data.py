# # This class object serves as storage for linked lists containing various info, analyzed from the data.
# # To be written to database.
#
# STRUCTURE:
# data = {
#     "samples": {
#         "sample_id_1": {
#             "mutations": {
#                 "mutation_id_1": {
#                     "transcript_id": "transcript_id_123",
#                     "annotation_info": {
#                         "variant_type": "missense",
#                         "functional_impact": "moderate",
#                         "pathogenicity": "likely_pathogenic",
#                         "additional_info": {
#                             "key1": "value1",
#                             "key2": "value2",
#                             ...
#                         }
#                     },
#                     "peptide_ids": {
#                         "peptide_id_111": {
#                             "binding_affinity": 75,
#                             "presentation_score": 8,
#                             ...
#                         },
#                         "peptide_id_112": {
#                             "binding_affinity": 92,
#                             "presentation_score": 6,
#                             ...
#                         },
#                         ...
#                     }
#                 },
#                 ...
#             }
#         },
#         ...
#     },
#     "transcripts": {
#         "transcript_id_123": {
#             "gene_symbol": "GENE1",
#             "transcript_length": 1025,
#             "exons": 5,
#             "chromosome": "chrX",
#             "strand": "+",
#             "additional_info": {
#                 "key1": "value1",
#                 "key2": "value2",
#                 ...
#             }
#         },
#         "transcript_id_124": {
#             "gene_symbol": "GENE2",
#             "transcript_length": 1300,
#             "exons": 8,
#             "chromosome": "chr1",
#             "strand": "-",
#             "additional_info": {
#                 "key1": "value1",
#                 "key2": "value2",
#                 ...
#             }
#         },
#         ...
#     },
#     ...
# }


#    To get all the mutations for a specific sample: data["samples"]["sample_id_1"]["mutations"]
#    To get the transcript ID for a specific mutation: data["samples"]["sample_id_1"]["mutations"]["mutation_id_1"]["transcript_id"]
#    binding_affinity = data["samples"]["sample_id_1"]["mutations"]["mutation_id_1"]["peptide_ids"]["peptide_id_111"]["binding_affinity"]
#    presentation_score = data["samples"]["sample_id_1"]["mutations"]["mutation_id_1"]["peptide_ids"]["peptide_id_111"]["presentation_score"]



import pandas as pd


class PipelineData:
    def __init__(self):
        pass

