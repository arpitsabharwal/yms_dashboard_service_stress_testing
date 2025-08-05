import csv
import itertools
import requests
import sys
import json

# ==============================================================================
# 1. DEFINE YOUR TENANT-SPECIFIC DATA
# ==============================================================================
# Customize this section with your actual tenant data.

# how to get facility_ids and carrier_ids:
# - Use the API to fetch facility and carrier data for each tenant.
# - Replace the placeholder values with actual IDs and tokens.


LOCAL = "http://api-proxy:8000"
DEV = "https://dy-dev.fourkites.com"
QAT = "https://dy-qat.fourkites.com"
STRESS = "https://dy-stress.fourkites.com"
STAGING = "https://dy-staging.fourkites.com"
PROD = "https://dy.fourkites.com"


TENANTS_AUTH_TOKEN = {
    # "shipperapi": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTQ3VrdDB3V1dwOUpGa0xNcHhCX21oYUJ6SDBIclNhMDZFLWtiWUN6NklnIn0.eyJleHAiOjE3NTQzNDA2MjQsImlhdCI6MTc1NDI4MzA0MSwiYXV0aF90aW1lIjoxNzU0MjgzMDI0LCJqdGkiOiI1Zjk4M2JhMy0wYmQ2LTRlNTUtYjFmNC0zYjM0Y2RlOTYwNGUiLCJpc3MiOiJodHRwczovL2R5LXN0cmVzcy5mb3Vya2l0ZXMuY29tL2tleWNsb2FrL3JlYWxtcy9ZTVMiLCJzdWIiOiI0ZmE4NmE0ZS1mOWRmLTRjMjktYWYzZS0yMmJhNTBhYzBiYjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ5bXN1aSIsIm5vbmNlIjoiM2IzNjM0MzMtOGQ2YS00MDQ2LThmYWUtYjlkY2RhYTJjNTlkIiwic2Vzc2lvbl9zdGF0ZSI6IjYyNDM2NWQzLTBlODktNGIyZC04NmEyLWQwOGYxMWU1Zjg2ZiIsImFjciI6IjEiLCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwidGVuYW50X2lkIjoic2hpcHBlcmFwaSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicGVybWlzc2lvbnMiOlsicmVhZF9sb2Fkc19hcGkiLCJtb2RpZnlfdG1zX2FwaSIsInJlYWRfc3dpdGNoZXJfdmVoaWNsZXNfYXBpIiwicmVhZF9jYXJyaWVyc19hcGkiLCJtb2RpZnlfc3dpdGNoZXJfdmVoaWNsZXNfYXBpIiwicmVhZF9nYXRlX3Bhc3Nlc19hcGkiLCJtb2RpZnlfeWFyZF9wcm9wZXJ0aWVzX2FwaSIsIm1vZGlmeV9hcHBvaW50bWVudHNfYXBpIiwibW9kaWZ5X3dtc19hcGkiLCJtb2RpZnlfdXNlcnNfYXBpIiwibW9kaWZ5X3J1bGVzX2FwaSIsIm1vZGlmeV90cmFpbGVyc19hcGkiLCJyZWFkX2dhdGVfZ3VhcmRzX2FwaSIsInJlYWRfZGVsaXZlcmllc19hcGkiLCJyZWFkX21vdmVfcmVxdWVzdHNfYXBpIiwibW9kaWZ5X3RyYWlsZXJfdGFnc19hcGkiLCJ1bWFfYXV0aG9yaXphdGlvbiIsInJlYWRfY3RwYXRfc2V0dGluZ3MiLCJyZWFkX3dlYmhvb2tzX2FwaSIsInJlYWRfZ2F0ZXNfYXBpIiwicmVhZF9jYXJyaWVyX3NpdGVzX2VsaWdpYmlsaXR5IiwicmVhZF9zaXRlX2xldmVsX2NvbnRyb2wiLCJyZWFkX2N1c3RvbV9maWVsZHNfYXBpIiwibW9kaWZ5X2N0cGF0X3NldHRpbmdzIiwibW9kaWZ5X2NhcnJpZXJzX2FwaSIsIm1vZGlmeV9zaXRlc19hcGkiLCJtb2RpZnlfY3VzdG9tX2ZpZWxkc19hcGkiLCJzdXBlcl9hZG1pbl9hcGkiLCJtb2RpZnlfZGVsaXZlcmllc19hcGkiLCJtb2RpZnlfYWRkcmVzc2VzX2FwaSIsIm1vZGlmeV9lbWVyZ2VuY3lfbWVzc2FnZV9hcGkiLCJyZWFkX3RyYWlsZXJfbGlzdF9hcGkiLCJtb2RpZnlfc3dpdGNoZXJzX2FwaSIsInJlYWRfdHJhaWxlcl9jaGVja3NfYXBpIiwibW9kaWZ5X2FsbF91c2Vyc19hcGkiLCJyZWFkX3RyYWlsZXJzX2FwaSIsIm1vZGlmeV9hdXRoX2NsaWVudHNfYXBpIiwibW9kaWZ5X3RyYWlsZXJfbGlzdF9hdWRpdF9hcGkiLCJtb2RpZnlfY3VzdG9tZXJzX2FwaSIsInNoYXJlZF9yZXBvcnRfY3JlYXRlX2FwaSIsInJlYWRfYWxsX3VzZXJzX2FwaSIsIm1vZGlmeV93ZWJob29rc19hcGkiLCJtb2RpZnlfb2NjdXBhbmN5X3NlbnNvcnNfYXBpIiwibW9kaWZ5X2xvYWRzX2FwaSIsIm1vZGlmeV9jYXJyaWVyX3NpdGVzX2VsaWdpYmlsaXR5IiwibW9kaWZ5X3JlcG9ydHNfYXBpIiwibW9kaWZ5X2dhdGVfcGFzc2VzX2FwaSIsIm1vZGlmeV90cmFpbGVyX2xpc3RfYXBpIiwibW9kaWZ5X3NpdGVfbGljZW5zZXNfYXBpIiwicmVhZF9jdXN0b21lcnNfYXBpIiwicmVhZF9raW9za19oZWxwY29kZV9hcGkiLCJyZWFkX3JlY3VycmluZ19kZWxpdmVyaWVzX2FwaSIsInJlYWRfdXNlcnNfYXBpIiwicmVhZF9hZGRyZXNzZXNfYXBpIiwicmVhZF9ydWxlc19hcGkiLCJtb2RpZnlfZ2F0ZXNfYXBpIiwibW9kaWZ5X21vdmVfcmVxdWVzdHNfYXBpIiwib2ZmbGluZV9hY2Nlc3MiLCJtb2RpZnlfZnJlaWdodF9hcGkiLCJyZWFkX3lhcmRfcHJvcGVydGllc19hcGkiLCJtaWdyYXRpb25zLXZlcnNpb24teW1zLWFwaSIsImZvdXJraXRlc19pbnRlcm5hbF9hcGkiLCJyZWFkX3NpdGVzX2FwaSIsIm1vZGlmeV9nYXRlX2d1YXJkc19hcGkiLCJyZWFkX3RyYWlsZXJfdGFnc19hcGkiLCJtb2RpZnlfcmVjdXJyaW5nX2RlbGl2ZXJpZXNfYXBpIiwibW9kaWZ5X2dhdGVfYXBpIiwicmVhZF9sb2NhdGlvbnNfYXBpIiwicmVhZF9hcHBvaW50bWVudHNfYXBpIiwicmVhZF9mcmVpZ2h0X2FwaSIsInJlYWRfc2F2ZWRfZmlsdGVyc19hcGkiLCJtb2RpZnlfc2NoZWR1bGVzX2FwaSIsInNoYXJlZF9yZXBvcnRfYWRtaW5fYXBpIiwibW9kaWZ5X2xvY2F0aW9uc19hcGkiLCJyZWFkX3JlcG9ydHNfYXBpIiwicmVhZF9lcnBfc3VibWlzc2lvbnNfYXBpIiwibW9kaWZ5X3NhdmVkX2ZpbHRlcnNfYXBpIiwibW9kaWZ5X2VycF9zdWJtaXNzaW9uc19hcGkiLCJyZWFkX3NjaGVkdWxlc19hcGkiLCJtb2RpZnlfc2l0ZV9sZXZlbF9jb250cm9sIiwibW9kaWZ5X3RyYWlsZXJfY2hlY2tzX2FwaSIsInRlbmFudF92YWxpZGF0aW9uX25vdF9yZXF1aXJlZCIsInJlYWRfb2NjdXBhbmN5X3NlbnNvcnNfYXBpIl0sIm5hbWUiOiJBcnBpdCBTYWJoYXJ3YWwiLCJncm91cHMiOlsiT09TIENvbnRyb2wiLCJTZWN1cml0eSIsIlN1cGVyIEFkbWluIl0sInByZWZlcnJlZF91c2VybmFtZSI6ImFycGl0LnNhYmhhcndhbEBmb3Vya2l0ZXMuY29tIiwiZ2l2ZW5fbmFtZSI6IkFycGl0IiwiZmFtaWx5X25hbWUiOiJTYWJoYXJ3YWwifQ.qaP2lN9ZifYoVzm8oJKiQYMKwUqLFUzFUQhZQa8bnHtkz7FobDqZ1ge0qC3E4LeARGctRppI3xCtmr6Y6lTqAJh1_g4ZmxlIcacG4kMpsZWIJ2iCZwt6dO1XItX-hsUfB5a7VFCqFnOgJRQ4eYtagda1Tj9jWIjfHLqDY1we37DZpOYmYXjmi0bS-Ar81pp2qMDKfNS3BY6sjzCaZkeP-wbbWey7IWLl2S43E4bk9i7tYwvxxNH8t0KT48YQeWLwO1qjfvoWF2x0spzjbRJGF9KmIYxYNPHhJGC1PCcNpgP4JLRZvNmWcpXOV5bC9fY3VBckxOTMXZ_kp04S8qAnLQ",
    "ge-appliances": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTQ3VrdDB3V1dwOUpGa0xNcHhCX21oYUJ6SDBIclNhMDZFLWtiWUN6NklnIn0.eyJleHAiOjE3NTQ0MTkwMjUsImlhdCI6MTc1NDM2MTYwNCwiYXV0aF90aW1lIjoxNzU0MzYxNDI1LCJqdGkiOiJkMDMxZGY5ZS0yODU4LTRhNjktYmRhOS0zNmIzYjU1YTA4MTgiLCJpc3MiOiJodHRwczovL2R5LXN0cmVzcy5mb3Vya2l0ZXMuY29tL2tleWNsb2FrL3JlYWxtcy9ZTVMiLCJzdWIiOiI0ZmE4NmE0ZS1mOWRmLTRjMjktYWYzZS0yMmJhNTBhYzBiYjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ5bXN1aSIsIm5vbmNlIjoiNDcwYzQwMGQtNzMyZS00YTIzLTgzZDctODJlYzA0MTcyNjFiIiwic2Vzc2lvbl9zdGF0ZSI6IjRkZmI4MmE4LTE1NTktNDE3ZS04ODMyLTZlYmE2YzA5ZDdlNCIsImFjciI6IjAiLCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwidGVuYW50X2lkIjoiZ2UtYXBwbGlhbmNlcyIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicGVybWlzc2lvbnMiOlsicmVhZF9sb2Fkc19hcGkiLCJtb2RpZnlfdG1zX2FwaSIsInJlYWRfc3dpdGNoZXJfdmVoaWNsZXNfYXBpIiwicmVhZF9jYXJyaWVyc19hcGkiLCJtb2RpZnlfc3dpdGNoZXJfdmVoaWNsZXNfYXBpIiwicmVhZF9nYXRlX3Bhc3Nlc19hcGkiLCJtb2RpZnlfeWFyZF9wcm9wZXJ0aWVzX2FwaSIsIm1vZGlmeV9hcHBvaW50bWVudHNfYXBpIiwibW9kaWZ5X3dtc19hcGkiLCJtb2RpZnlfdXNlcnNfYXBpIiwibW9kaWZ5X3J1bGVzX2FwaSIsIm1vZGlmeV90cmFpbGVyc19hcGkiLCJyZWFkX2dhdGVfZ3VhcmRzX2FwaSIsInJlYWRfZGVsaXZlcmllc19hcGkiLCJyZWFkX21vdmVfcmVxdWVzdHNfYXBpIiwibW9kaWZ5X3RyYWlsZXJfdGFnc19hcGkiLCJ1bWFfYXV0aG9yaXphdGlvbiIsInJlYWRfY3RwYXRfc2V0dGluZ3MiLCJyZWFkX3dlYmhvb2tzX2FwaSIsInJlYWRfZ2F0ZXNfYXBpIiwicmVhZF9jYXJyaWVyX3NpdGVzX2VsaWdpYmlsaXR5IiwicmVhZF9zaXRlX2xldmVsX2NvbnRyb2wiLCJyZWFkX2N1c3RvbV9maWVsZHNfYXBpIiwibW9kaWZ5X2N0cGF0X3NldHRpbmdzIiwibW9kaWZ5X2NhcnJpZXJzX2FwaSIsIm1vZGlmeV9zaXRlc19hcGkiLCJtb2RpZnlfY3VzdG9tX2ZpZWxkc19hcGkiLCJzdXBlcl9hZG1pbl9hcGkiLCJtb2RpZnlfZGVsaXZlcmllc19hcGkiLCJtb2RpZnlfYWRkcmVzc2VzX2FwaSIsIm1vZGlmeV9lbWVyZ2VuY3lfbWVzc2FnZV9hcGkiLCJyZWFkX3RyYWlsZXJfbGlzdF9hcGkiLCJtb2RpZnlfc3dpdGNoZXJzX2FwaSIsInJlYWRfdHJhaWxlcl9jaGVja3NfYXBpIiwibW9kaWZ5X2FsbF91c2Vyc19hcGkiLCJyZWFkX3RyYWlsZXJzX2FwaSIsIm1vZGlmeV9hdXRoX2NsaWVudHNfYXBpIiwibW9kaWZ5X3RyYWlsZXJfbGlzdF9hdWRpdF9hcGkiLCJtb2RpZnlfY3VzdG9tZXJzX2FwaSIsInNoYXJlZF9yZXBvcnRfY3JlYXRlX2FwaSIsInJlYWRfYWxsX3VzZXJzX2FwaSIsIm1vZGlmeV93ZWJob29rc19hcGkiLCJtb2RpZnlfb2NjdXBhbmN5X3NlbnNvcnNfYXBpIiwibW9kaWZ5X2xvYWRzX2FwaSIsIm1vZGlmeV9jYXJyaWVyX3NpdGVzX2VsaWdpYmlsaXR5IiwibW9kaWZ5X3JlcG9ydHNfYXBpIiwibW9kaWZ5X2dhdGVfcGFzc2VzX2FwaSIsIm1vZGlmeV90cmFpbGVyX2xpc3RfYXBpIiwibW9kaWZ5X3NpdGVfbGljZW5zZXNfYXBpIiwicmVhZF9jdXN0b21lcnNfYXBpIiwicmVhZF9raW9za19oZWxwY29kZV9hcGkiLCJyZWFkX3JlY3VycmluZ19kZWxpdmVyaWVzX2FwaSIsInJlYWRfdXNlcnNfYXBpIiwicmVhZF9hZGRyZXNzZXNfYXBpIiwicmVhZF9ydWxlc19hcGkiLCJtb2RpZnlfZ2F0ZXNfYXBpIiwibW9kaWZ5X21vdmVfcmVxdWVzdHNfYXBpIiwib2ZmbGluZV9hY2Nlc3MiLCJtb2RpZnlfZnJlaWdodF9hcGkiLCJyZWFkX3lhcmRfcHJvcGVydGllc19hcGkiLCJtaWdyYXRpb25zLXZlcnNpb24teW1zLWFwaSIsImZvdXJraXRlc19pbnRlcm5hbF9hcGkiLCJyZWFkX3NpdGVzX2FwaSIsIm1vZGlmeV9nYXRlX2d1YXJkc19hcGkiLCJyZWFkX3RyYWlsZXJfdGFnc19hcGkiLCJtb2RpZnlfcmVjdXJyaW5nX2RlbGl2ZXJpZXNfYXBpIiwibW9kaWZ5X2dhdGVfYXBpIiwicmVhZF9sb2NhdGlvbnNfYXBpIiwicmVhZF9hcHBvaW50bWVudHNfYXBpIiwicmVhZF9mcmVpZ2h0X2FwaSIsInJlYWRfc2F2ZWRfZmlsdGVyc19hcGkiLCJtb2RpZnlfc2NoZWR1bGVzX2FwaSIsInNoYXJlZF9yZXBvcnRfYWRtaW5fYXBpIiwibW9kaWZ5X2xvY2F0aW9uc19hcGkiLCJyZWFkX3JlcG9ydHNfYXBpIiwicmVhZF9lcnBfc3VibWlzc2lvbnNfYXBpIiwibW9kaWZ5X3NhdmVkX2ZpbHRlcnNfYXBpIiwibW9kaWZ5X2VycF9zdWJtaXNzaW9uc19hcGkiLCJyZWFkX3NjaGVkdWxlc19hcGkiLCJtb2RpZnlfc2l0ZV9sZXZlbF9jb250cm9sIiwibW9kaWZ5X3RyYWlsZXJfY2hlY2tzX2FwaSIsInRlbmFudF92YWxpZGF0aW9uX25vdF9yZXF1aXJlZCIsInJlYWRfb2NjdXBhbmN5X3NlbnNvcnNfYXBpIl0sIm5hbWUiOiJBcnBpdCBTYWJoYXJ3YWwiLCJncm91cHMiOlsiT09TIENvbnRyb2wiLCJTZWN1cml0eSIsIlN1cGVyIEFkbWluIl0sInByZWZlcnJlZF91c2VybmFtZSI6ImFycGl0LnNhYmhhcndhbEBmb3Vya2l0ZXMuY29tIiwiZ2l2ZW5fbmFtZSI6IkFycGl0IiwiZmFtaWx5X25hbWUiOiJTYWJoYXJ3YWwifQ.QLqS_7ml1BgNCWStselPtgRixh6JexO8wtPJaI5AfwpJXP4ndOshssuCkT98QcOUB0Hn0EuI7PO9QRVbDqNsS7IrSbnm2JCtUoyuPMRxcucSY5_BQkJ5e34MjYMyoFELUvJ_1Jj4VDO72DExDksL5IkV79-GIBEPSFYVfPqN38XHGllzG17wtjl5SVAaF1Ykdqmki205uXSJ2JUo9xR-Rezl4Snh_18q_iwazeEsi3_b394dhOtWK25wZOQETCiqEHDi-RFMrCa4Ss4JpzMBfZnsJQLchvwbTlVtnPprWypUMeNKEQsJ_eQc_kOqb83FEBuZuvTiWJzH8a8qZt2Jaw",
    "fritolay": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTQ3VrdDB3V1dwOUpGa0xNcHhCX21oYUJ6SDBIclNhMDZFLWtiWUN6NklnIn0.eyJleHAiOjE3NTQ0MTkwMjUsImlhdCI6MTc1NDM2MTU1OCwiYXV0aF90aW1lIjoxNzU0MzYxNDI1LCJqdGkiOiIyODc4ZDBjYy1hZmQyLTRiNjAtYTY1ZC0wZjczOTYyMDhmMTkiLCJpc3MiOiJodHRwczovL2R5LXN0cmVzcy5mb3Vya2l0ZXMuY29tL2tleWNsb2FrL3JlYWxtcy9ZTVMiLCJzdWIiOiI0ZmE4NmE0ZS1mOWRmLTRjMjktYWYzZS0yMmJhNTBhYzBiYjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ5bXN1aSIsIm5vbmNlIjoiMDlhNTBiZjYtOTFlNS00Y2EwLTk2MmEtZWU5NWI2MzcxNDVmIiwic2Vzc2lvbl9zdGF0ZSI6IjRkZmI4MmE4LTE1NTktNDE3ZS04ODMyLTZlYmE2YzA5ZDdlNCIsImFjciI6IjAiLCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwidGVuYW50X2lkIjoiZnJpdG9sYXkiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInBlcm1pc3Npb25zIjpbInJlYWRfbG9hZHNfYXBpIiwibW9kaWZ5X3Rtc19hcGkiLCJyZWFkX3N3aXRjaGVyX3ZlaGljbGVzX2FwaSIsInJlYWRfY2FycmllcnNfYXBpIiwibW9kaWZ5X3N3aXRjaGVyX3ZlaGljbGVzX2FwaSIsInJlYWRfZ2F0ZV9wYXNzZXNfYXBpIiwibW9kaWZ5X3lhcmRfcHJvcGVydGllc19hcGkiLCJtb2RpZnlfYXBwb2ludG1lbnRzX2FwaSIsIm1vZGlmeV93bXNfYXBpIiwibW9kaWZ5X3VzZXJzX2FwaSIsIm1vZGlmeV9ydWxlc19hcGkiLCJtb2RpZnlfdHJhaWxlcnNfYXBpIiwicmVhZF9nYXRlX2d1YXJkc19hcGkiLCJyZWFkX2RlbGl2ZXJpZXNfYXBpIiwicmVhZF9tb3ZlX3JlcXVlc3RzX2FwaSIsIm1vZGlmeV90cmFpbGVyX3RhZ3NfYXBpIiwidW1hX2F1dGhvcml6YXRpb24iLCJyZWFkX2N0cGF0X3NldHRpbmdzIiwicmVhZF93ZWJob29rc19hcGkiLCJyZWFkX2dhdGVzX2FwaSIsInJlYWRfY2Fycmllcl9zaXRlc19lbGlnaWJpbGl0eSIsInJlYWRfc2l0ZV9sZXZlbF9jb250cm9sIiwicmVhZF9jdXN0b21fZmllbGRzX2FwaSIsIm1vZGlmeV9jdHBhdF9zZXR0aW5ncyIsIm1vZGlmeV9jYXJyaWVyc19hcGkiLCJtb2RpZnlfc2l0ZXNfYXBpIiwibW9kaWZ5X2N1c3RvbV9maWVsZHNfYXBpIiwic3VwZXJfYWRtaW5fYXBpIiwibW9kaWZ5X2RlbGl2ZXJpZXNfYXBpIiwibW9kaWZ5X2FkZHJlc3Nlc19hcGkiLCJtb2RpZnlfZW1lcmdlbmN5X21lc3NhZ2VfYXBpIiwicmVhZF90cmFpbGVyX2xpc3RfYXBpIiwibW9kaWZ5X3N3aXRjaGVyc19hcGkiLCJyZWFkX3RyYWlsZXJfY2hlY2tzX2FwaSIsIm1vZGlmeV9hbGxfdXNlcnNfYXBpIiwicmVhZF90cmFpbGVyc19hcGkiLCJtb2RpZnlfYXV0aF9jbGllbnRzX2FwaSIsIm1vZGlmeV90cmFpbGVyX2xpc3RfYXVkaXRfYXBpIiwibW9kaWZ5X2N1c3RvbWVyc19hcGkiLCJzaGFyZWRfcmVwb3J0X2NyZWF0ZV9hcGkiLCJyZWFkX2FsbF91c2Vyc19hcGkiLCJtb2RpZnlfd2ViaG9va3NfYXBpIiwibW9kaWZ5X29jY3VwYW5jeV9zZW5zb3JzX2FwaSIsIm1vZGlmeV9sb2Fkc19hcGkiLCJtb2RpZnlfY2Fycmllcl9zaXRlc19lbGlnaWJpbGl0eSIsIm1vZGlmeV9yZXBvcnRzX2FwaSIsIm1vZGlmeV9nYXRlX3Bhc3Nlc19hcGkiLCJtb2RpZnlfdHJhaWxlcl9saXN0X2FwaSIsIm1vZGlmeV9zaXRlX2xpY2Vuc2VzX2FwaSIsInJlYWRfY3VzdG9tZXJzX2FwaSIsInJlYWRfa2lvc2tfaGVscGNvZGVfYXBpIiwicmVhZF9yZWN1cnJpbmdfZGVsaXZlcmllc19hcGkiLCJyZWFkX3VzZXJzX2FwaSIsInJlYWRfYWRkcmVzc2VzX2FwaSIsInJlYWRfcnVsZXNfYXBpIiwibW9kaWZ5X2dhdGVzX2FwaSIsIm1vZGlmeV9tb3ZlX3JlcXVlc3RzX2FwaSIsIm9mZmxpbmVfYWNjZXNzIiwibW9kaWZ5X2ZyZWlnaHRfYXBpIiwicmVhZF95YXJkX3Byb3BlcnRpZXNfYXBpIiwibWlncmF0aW9ucy12ZXJzaW9uLXltcy1hcGkiLCJmb3Vya2l0ZXNfaW50ZXJuYWxfYXBpIiwicmVhZF9zaXRlc19hcGkiLCJtb2RpZnlfZ2F0ZV9ndWFyZHNfYXBpIiwicmVhZF90cmFpbGVyX3RhZ3NfYXBpIiwibW9kaWZ5X3JlY3VycmluZ19kZWxpdmVyaWVzX2FwaSIsIm1vZGlmeV9nYXRlX2FwaSIsInJlYWRfbG9jYXRpb25zX2FwaSIsInJlYWRfYXBwb2ludG1lbnRzX2FwaSIsInJlYWRfZnJlaWdodF9hcGkiLCJyZWFkX3NhdmVkX2ZpbHRlcnNfYXBpIiwibW9kaWZ5X3NjaGVkdWxlc19hcGkiLCJzaGFyZWRfcmVwb3J0X2FkbWluX2FwaSIsIm1vZGlmeV9sb2NhdGlvbnNfYXBpIiwicmVhZF9yZXBvcnRzX2FwaSIsInJlYWRfZXJwX3N1Ym1pc3Npb25zX2FwaSIsIm1vZGlmeV9zYXZlZF9maWx0ZXJzX2FwaSIsIm1vZGlmeV9lcnBfc3VibWlzc2lvbnNfYXBpIiwicmVhZF9zY2hlZHVsZXNfYXBpIiwibW9kaWZ5X3NpdGVfbGV2ZWxfY29udHJvbCIsIm1vZGlmeV90cmFpbGVyX2NoZWNrc19hcGkiLCJ0ZW5hbnRfdmFsaWRhdGlvbl9ub3RfcmVxdWlyZWQiLCJyZWFkX29jY3VwYW5jeV9zZW5zb3JzX2FwaSJdLCJuYW1lIjoiQXJwaXQgUyIsImdyb3VwcyI6WyJPT1MgQ29udHJvbCIsIlNlY3VyaXR5IiwiU3VwZXIgQWRtaW4iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYXJwaXQuc2FiaGFyd2FsQGZvdXJraXRlcy5jb20iLCJnaXZlbl9uYW1lIjoiQXJwaXQiLCJmYW1pbHlfbmFtZSI6IlMifQ.a3L_TeQ9dPHDZb9vk5A7C0bIcFS2JrN0WbJBXUNflIvpyzpxJt-5E6kwKvjUwnRuZxOUduQjpSQyaDGQokBSB5pcbpPS6VEhakMMcn8xzaX5HURsf2DLj7bLLbUAsqhWy8y5eEs-3ebLy2uN9YJl5Fac0_Cj2FIrM_aOyn6cfqOwqMESVk9GWZnbjnyzrahZgtEAFXf2r64TzymnapNy5MPc5gO2N484QQP5T7fUe8aQlYV8bnc6AbCuN6VS_kNoaJiuQDoduPVobCSLnmEcVVMH1ar8ljXXjxsJ8HcHXW9igFKxDJRTkp4gxK6JOaI7mryg6vRQdEMlxc80JiMMEQ",
    "kimberly-clark-corporation": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTQ3VrdDB3V1dwOUpGa0xNcHhCX21oYUJ6SDBIclNhMDZFLWtiWUN6NklnIn0.eyJleHAiOjE3NTQ0MTkwMjUsImlhdCI6MTc1NDM2MTQyOCwiYXV0aF90aW1lIjoxNzU0MzYxNDI1LCJqdGkiOiJlZDYzOWQxOC1hYjE4LTRhMDgtOWE1My1mYTgzZTM3YjkxMWQiLCJpc3MiOiJodHRwczovL2R5LXN0cmVzcy5mb3Vya2l0ZXMuY29tL2tleWNsb2FrL3JlYWxtcy9ZTVMiLCJzdWIiOiI0ZmE4NmE0ZS1mOWRmLTRjMjktYWYzZS0yMmJhNTBhYzBiYjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ5bXN1aSIsIm5vbmNlIjoiZTljYzY1M2UtZDgxMi00OTE5LTg3ZWUtM2I3YjgyNTVlN2UwIiwic2Vzc2lvbl9zdGF0ZSI6IjRkZmI4MmE4LTE1NTktNDE3ZS04ODMyLTZlYmE2YzA5ZDdlNCIsImFjciI6IjEiLCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwidGVuYW50X2lkIjoia2ltYmVybHktY2xhcmstY29ycG9yYXRpb24iLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInBlcm1pc3Npb25zIjpbInJlYWRfbG9hZHNfYXBpIiwibW9kaWZ5X3Rtc19hcGkiLCJyZWFkX3N3aXRjaGVyX3ZlaGljbGVzX2FwaSIsInJlYWRfY2FycmllcnNfYXBpIiwibW9kaWZ5X3N3aXRjaGVyX3ZlaGljbGVzX2FwaSIsInJlYWRfZ2F0ZV9wYXNzZXNfYXBpIiwibW9kaWZ5X3lhcmRfcHJvcGVydGllc19hcGkiLCJtb2RpZnlfYXBwb2ludG1lbnRzX2FwaSIsIm1vZGlmeV93bXNfYXBpIiwibW9kaWZ5X3VzZXJzX2FwaSIsIm1vZGlmeV9ydWxlc19hcGkiLCJtb2RpZnlfdHJhaWxlcnNfYXBpIiwicmVhZF9nYXRlX2d1YXJkc19hcGkiLCJyZWFkX2RlbGl2ZXJpZXNfYXBpIiwicmVhZF9tb3ZlX3JlcXVlc3RzX2FwaSIsIm1vZGlmeV90cmFpbGVyX3RhZ3NfYXBpIiwidW1hX2F1dGhvcml6YXRpb24iLCJyZWFkX2N0cGF0X3NldHRpbmdzIiwicmVhZF93ZWJob29rc19hcGkiLCJyZWFkX2dhdGVzX2FwaSIsInJlYWRfY2Fycmllcl9zaXRlc19lbGlnaWJpbGl0eSIsInJlYWRfc2l0ZV9sZXZlbF9jb250cm9sIiwicmVhZF9jdXN0b21fZmllbGRzX2FwaSIsIm1vZGlmeV9jdHBhdF9zZXR0aW5ncyIsIm1vZGlmeV9jYXJyaWVyc19hcGkiLCJtb2RpZnlfc2l0ZXNfYXBpIiwibW9kaWZ5X2N1c3RvbV9maWVsZHNfYXBpIiwic3VwZXJfYWRtaW5fYXBpIiwibW9kaWZ5X2RlbGl2ZXJpZXNfYXBpIiwibW9kaWZ5X2FkZHJlc3Nlc19hcGkiLCJtb2RpZnlfZW1lcmdlbmN5X21lc3NhZ2VfYXBpIiwicmVhZF90cmFpbGVyX2xpc3RfYXBpIiwibW9kaWZ5X3N3aXRjaGVyc19hcGkiLCJyZWFkX3RyYWlsZXJfY2hlY2tzX2FwaSIsIm1vZGlmeV9hbGxfdXNlcnNfYXBpIiwicmVhZF90cmFpbGVyc19hcGkiLCJtb2RpZnlfYXV0aF9jbGllbnRzX2FwaSIsIm1vZGlmeV90cmFpbGVyX2xpc3RfYXVkaXRfYXBpIiwibW9kaWZ5X2N1c3RvbWVyc19hcGkiLCJzaGFyZWRfcmVwb3J0X2NyZWF0ZV9hcGkiLCJyZWFkX2FsbF91c2Vyc19hcGkiLCJtb2RpZnlfd2ViaG9va3NfYXBpIiwibW9kaWZ5X29jY3VwYW5jeV9zZW5zb3JzX2FwaSIsIm1vZGlmeV9sb2Fkc19hcGkiLCJtb2RpZnlfY2Fycmllcl9zaXRlc19lbGlnaWJpbGl0eSIsIm1vZGlmeV9yZXBvcnRzX2FwaSIsIm1vZGlmeV9nYXRlX3Bhc3Nlc19hcGkiLCJtb2RpZnlfdHJhaWxlcl9saXN0X2FwaSIsIm1vZGlmeV9zaXRlX2xpY2Vuc2VzX2FwaSIsInJlYWRfY3VzdG9tZXJzX2FwaSIsInJlYWRfa2lvc2tfaGVscGNvZGVfYXBpIiwicmVhZF9yZWN1cnJpbmdfZGVsaXZlcmllc19hcGkiLCJyZWFkX3VzZXJzX2FwaSIsInJlYWRfYWRkcmVzc2VzX2FwaSIsInJlYWRfcnVsZXNfYXBpIiwibW9kaWZ5X2dhdGVzX2FwaSIsIm1vZGlmeV9tb3ZlX3JlcXVlc3RzX2FwaSIsIm9mZmxpbmVfYWNjZXNzIiwibW9kaWZ5X2ZyZWlnaHRfYXBpIiwicmVhZF95YXJkX3Byb3BlcnRpZXNfYXBpIiwibWlncmF0aW9ucy12ZXJzaW9uLXltcy1hcGkiLCJmb3Vya2l0ZXNfaW50ZXJuYWxfYXBpIiwicmVhZF9zaXRlc19hcGkiLCJtb2RpZnlfZ2F0ZV9ndWFyZHNfYXBpIiwicmVhZF90cmFpbGVyX3RhZ3NfYXBpIiwibW9kaWZ5X3JlY3VycmluZ19kZWxpdmVyaWVzX2FwaSIsIm1vZGlmeV9nYXRlX2FwaSIsInJlYWRfbG9jYXRpb25zX2FwaSIsInJlYWRfYXBwb2ludG1lbnRzX2FwaSIsInJlYWRfZnJlaWdodF9hcGkiLCJyZWFkX3NhdmVkX2ZpbHRlcnNfYXBpIiwibW9kaWZ5X3NjaGVkdWxlc19hcGkiLCJzaGFyZWRfcmVwb3J0X2FkbWluX2FwaSIsIm1vZGlmeV9sb2NhdGlvbnNfYXBpIiwicmVhZF9yZXBvcnRzX2FwaSIsInJlYWRfZXJwX3N1Ym1pc3Npb25zX2FwaSIsIm1vZGlmeV9zYXZlZF9maWx0ZXJzX2FwaSIsIm1vZGlmeV9lcnBfc3VibWlzc2lvbnNfYXBpIiwicmVhZF9zY2hlZHVsZXNfYXBpIiwibW9kaWZ5X3NpdGVfbGV2ZWxfY29udHJvbCIsIm1vZGlmeV90cmFpbGVyX2NoZWNrc19hcGkiLCJ0ZW5hbnRfdmFsaWRhdGlvbl9ub3RfcmVxdWlyZWQiLCJyZWFkX29jY3VwYW5jeV9zZW5zb3JzX2FwaSJdLCJuYW1lIjoiQXJwaXQgU2FiaGFyd2FsIiwiZ3JvdXBzIjpbIk9PUyBDb250cm9sIiwiU2VjdXJpdHkiLCJTdXBlciBBZG1pbiJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhcnBpdC5zYWJoYXJ3YWxAZm91cmtpdGVzLmNvbSIsImdpdmVuX25hbWUiOiJBcnBpdCIsImZhbWlseV9uYW1lIjoiU2FiaGFyd2FsIn0.bkWHhhxKuw_RDa4-VRCyEIABYN2z44j0Yfwv-sHMFDdZimJYo_u3l2V6hhVdZRwe16Vjaymksj3znI4qf9W5qMYQ8OKA752TK8zRMsIZhFD-yHy6sOfFC5c5fpbj2kwLfxo_hRNPvufkNdBjO6Wpn4hY7BT-r60cw_qLgm-wvS7NvJfN4318RgRRC7aRwqdGUIllLxtxK1fwQcEjW6DMJx_10NYRt34OyMfOTZH061AN_5TB3DwhwUaBubIatG-GfTAiL29f4zwnrUqHyR3Cy5nfjMsTFX3wdOHS9R8igZbsQZ6EBeF6YVC6G0gLLcL80ufgEvEoMJzO3rV_D8OvMg",
    # "sazerac": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTQ3VrdDB3V1dwOUpGa0xNcHhCX21oYUJ6SDBIclNhMDZFLWtiWUN6NklnIn0.eyJleHAiOjE3NTM5MzEwOTUsImlhdCI6MTc1Mzg3NjQ4NywiYXV0aF90aW1lIjoxNzUzODczNDk1LCJqdGkiOiI1MTJkN2JkOS0zOTJhLTRiNmItYTkyMC1mZWEyNWU0YzE5ZjUiLCJpc3MiOiJodHRwczovL2R5LXN0cmVzcy5mb3Vya2l0ZXMuY29tL2tleWNsb2FrL3JlYWxtcy9ZTVMiLCJzdWIiOiI0ZmE4NmE0ZS1mOWRmLTRjMjktYWYzZS0yMmJhNTBhYzBiYjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ5bXN1aSIsIm5vbmNlIjoiZDUwY2ViOTYtNTIxYi00NzAzLTgwNDAtZTQ3YmNmOGYyMTk5Iiwic2Vzc2lvbl9zdGF0ZSI6IjQzN2VlN2M4LTU0OGEtNGY5Yy1hZWQyLTRjMWMwZDUyYzAxZCIsImFjciI6IjAiLCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwidGVuYW50X2lkIjoia2ltYmVybHktY2xhcmstY29ycG9yYXRpb24iLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInBlcm1pc3Npb25zIjpbInJlYWRfbG9hZHNfYXBpIiwibW9kaWZ5X3Rtc19hcGkiLCJyZWFkX3N3aXRjaGVyX3ZlaGljbGVzX2FwaSIsInJlYWRfY2FycmllcnNfYXBpIiwibW9kaWZ5X3N3aXRjaGVyX3ZlaGljbGVzX2FwaSIsInJlYWRfZ2F0ZV9wYXNzZXNfYXBpIiwibW9kaWZ5X3lhcmRfcHJvcGVydGllc19hcGkiLCJtb2RpZnlfYXBwb2ludG1lbnRzX2FwaSIsIm1vZGlmeV93bXNfYXBpIiwibW9kaWZ5X3VzZXJzX2FwaSIsIm1vZGlmeV9ydWxlc19hcGkiLCJtb2RpZnlfdHJhaWxlcnNfYXBpIiwicmVhZF9nYXRlX2d1YXJkc19hcGkiLCJyZWFkX2RlbGl2ZXJpZXNfYXBpIiwicmVhZF9tb3ZlX3JlcXVlc3RzX2FwaSIsIm1vZGlmeV90cmFpbGVyX3RhZ3NfYXBpIiwidW1hX2F1dGhvcml6YXRpb24iLCJyZWFkX2N0cGF0X3NldHRpbmdzIiwicmVhZF93ZWJob29rc19hcGkiLCJyZWFkX2dhdGVzX2FwaSIsInJlYWRfY2Fycmllcl9zaXRlc19lbGlnaWJpbGl0eSIsInJlYWRfc2l0ZV9sZXZlbF9jb250cm9sIiwicmVhZF9jdXN0b21fZmllbGRzX2FwaSIsIm1vZGlmeV9jdHBhdF9zZXR0aW5ncyIsIm1vZGlmeV9jYXJyaWVyc19hcGkiLCJtb2RpZnlfc2l0ZXNfYXBpIiwibW9kaWZ5X2N1c3RvbV9maWVsZHNfYXBpIiwic3VwZXJfYWRtaW5fYXBpIiwibW9kaWZ5X2RlbGl2ZXJpZXNfYXBpIiwibW9kaWZ5X2FkZHJlc3Nlc19hcGkiLCJtb2RpZnlfZW1lcmdlbmN5X21lc3NhZ2VfYXBpIiwicmVhZF90cmFpbGVyX2xpc3RfYXBpIiwibW9kaWZ5X3N3aXRjaGVyc19hcGkiLCJyZWFkX3RyYWlsZXJfY2hlY2tzX2FwaSIsIm1vZGlmeV9hbGxfdXNlcnNfYXBpIiwicmVhZF90cmFpbGVyc19hcGkiLCJtb2RpZnlfYXV0aF9jbGllbnRzX2FwaSIsIm1vZGlmeV90cmFpbGVyX2xpc3RfYXVkaXRfYXBpIiwibW9kaWZ5X2N1c3RvbWVyc19hcGkiLCJzaGFyZWRfcmVwb3J0X2NyZWF0ZV9hcGkiLCJyZWFkX2FsbF91c2Vyc19hcGkiLCJtb2RpZnlfd2ViaG9va3NfYXBpIiwibW9kaWZ5X29jY3VwYW5jeV9zZW5zb3JzX2FwaSIsIm1vZGlmeV9sb2Fkc19hcGkiLCJtb2RpZnlfY2Fycmllcl9zaXRlc19lbGlnaWJpbGl0eSIsIm1vZGlmeV9yZXBvcnRzX2FwaSIsIm1vZGlmeV9nYXRlX3Bhc3Nlc19hcGkiLCJtb2RpZnlfdHJhaWxlcl9saXN0X2FwaSIsIm1vZGlmeV9zaXRlX2xpY2Vuc2VzX2FwaSIsInJlYWRfY3VzdG9tZXJzX2FwaSIsInJlYWRfa2lvc2tfaGVscGNvZGVfYXBpIiwicmVhZF9yZWN1cnJpbmdfZGVsaXZlcmllc19hcGkiLCJyZWFkX3VzZXJzX2FwaSIsInJlYWRfYWRkcmVzc2VzX2FwaSIsInJlYWRfcnVsZXNfYXBpIiwibW9kaWZ5X2dhdGVzX2FwaSIsIm1vZGlmeV9tb3ZlX3JlcXVlc3RzX2FwaSIsIm9mZmxpbmVfYWNjZXNzIiwibW9kaWZ5X2ZyZWlnaHRfYXBpIiwicmVhZF95YXJkX3Byb3BlcnRpZXNfYXBpIiwibWlncmF0aW9ucy12ZXJzaW9uLXltcy1hcGkiLCJmb3Vya2l0ZXNfaW50ZXJuYWxfYXBpIiwicmVhZF9zaXRlc19hcGkiLCJtb2RpZnlfZ2F0ZV9ndWFyZHNfYXBpIiwicmVhZF90cmFpbGVyX3RhZ3NfYXBpIiwibW9kaWZ5X3JlY3VycmluZ19kZWxpdmVyaWVzX2FwaSIsIm1vZGlmeV9nYXRlX2FwaSIsInJlYWRfbG9jYXRpb25zX2FwaSIsInJlYWRfYXBwb2ludG1lbnRzX2FwaSIsInJlYWRfZnJlaWdodF9hcGkiLCJyZWFkX3NhdmVkX2ZpbHRlcnNfYXBpIiwibW9kaWZ5X3NjaGVkdWxlc19hcGkiLCJzaGFyZWRfcmVwb3J0X2FkbWluX2FwaSIsIm1vZGlmeV9sb2NhdGlvbnNfYXBpIiwicmVhZF9yZXBvcnRzX2FwaSIsInJlYWRfZXJwX3N1Ym1pc3Npb25zX2FwaSIsIm1vZGlmeV9zYXZlZF9maWx0ZXJzX2FwaSIsIm1vZGlmeV9lcnBfc3VibWlzc2lvbnNfYXBpIiwicmVhZF9zY2hlZHVsZXNfYXBpIiwibW9kaWZ5X3NpdGVfbGV2ZWxfY29udHJvbCIsIm1vZGlmeV90cmFpbGVyX2NoZWNrc19hcGkiLCJ0ZW5hbnRfdmFsaWRhdGlvbl9ub3RfcmVxdWlyZWQiLCJyZWFkX29jY3VwYW5jeV9zZW5zb3JzX2FwaSJdLCJuYW1lIjoiQXJwaXQgUyIsImdyb3VwcyI6WyJPT1MgQ29udHJvbCIsIlNlY3VyaXR5IiwiU3VwZXIgQWRtaW4iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYXJwaXQuc2FiaGFyd2FsQGZvdXJraXRlcy5jb20iLCJnaXZlbl9uYW1lIjoiQXJwaXQiLCJmYW1pbHlfbmFtZSI6IlMifQ.JwZ7lTZI3Bz8Sx36AGlcmWB7lHJ3Mqf1ndPfwNrT4Ttqyb8Uu5OOxRP2E524W0tTeCAu_b1XidLwO6lUoysXyAhb9iGPgGzLTLA_jmoI3PeZprGX1v90mGpYH6bwoYnQdfo8NwmvGjop0ZItbC5I3xTQuJnv0HACtkTG4m8nxHvXOLwogfY_XswraTqRuh2SaKsYlDNW9hlA6uMTmvujUsH1OPD8QPdGC1qI3UvX73Vy7-aoVnI_MX-izh8jFvXVWwqOspgIJBPzxw0EhGMGe8xfa6-taqBHSeK4egwMD7krhLc7RQbWENdBfanGeJecM92M8PzD7WHc8DgyVMNJXg"
}
# ==============================================================================
# 2. DEFINE THE PARAMETERS FOR EACH API PAYLOAD
# ==============================================================================
# These are the pools of values to be combined for different API requests.
TRAILER_STATES = ["all", "noFlags", "audit", "damaged", "outOfService"]
SHIPMENT_DIRECTIONS = ["Inbound", "Outbound"]
THRESHOLD_HOURS = [12, 24, 48, 72]

# ==============================================================================
# 3. SCRIPT TO GENERATE THE EXHAUSTIVE CSV
# ==============================================================================
HEADER = [
    "api_endpoint", "tenantName", "facilityId", "authToken", "activeUsers", "rpmPerUser",
    "rampUpSeconds", "payload"
]

COUNTER = 5

def get_host_details():
    # accept a argument env which can be dev, local, qat, stress, staging, prod
    if len(sys.argv) < 2:
        print("Usage: python generate_exhaustive_data.py <env>")
        sys.exit(1)
    env = sys.argv[1].lower()
    if env == "local":
        return LOCAL
    elif env == "dev":
        return DEV
    elif env == "qat":
        return QAT
    elif env == "stress":
        return STRESS
    elif env == "staging":
        return STAGING
    elif env == "prod":
        return PROD
    """
    Add logic to fetch the host details based on the environment.
    This could involve reading from a configuration file or environment variables.
    """
    return LOCAL  # Default to local if no valid environment is provided

HOST = get_host_details()


def get_carrier_data_for_tenant(tenant_name, bearer_token):
    """
    Fetches the carrier data for a given tenant using the provided bearer token.
    This function should make an API call to retrieve the carrier IDs.
    """ 
    url = f"{HOST}/api/v1/carriers/"
    # call the api and get the data
    # This is a placeholder for the actual API call logic.
    # You would typically use requests or another HTTP library to make the call.
    # For example:
    response = requests.get(url, headers={"Authorization": bearer_token})
    if response.status_code == 200:
        print(f"Successfully fetched carrier IDs for tenant: {tenant_name}")
        carrier_ids = [carrier['id'] for carrier in response.json() if (carrier and carrier.get('id'))]
        return carrier_ids
    else:
        raise Exception(f"Failed to fetch carrier data for tenant {tenant_name}: {response.status_code}")


def get_licensed_facility_ids_for_tenant(tenant_name, bearer_token):
    """
    Fetches the licensed facility IDs for a given tenant using the provided bearer token.
    This function should make an API call to retrieve the facility IDs.
    """
    url = f"{HOST}/api/v1/sites/"
    # call the api and get the data
    # This is a placeholder for the actual API call logic.
    response = requests.get(url, headers={"Authorization": bearer_token})
    if response.status_code == 200:
        print(f"Successfully fetched facility IDs for tenant: {tenant_name}")
        site_ids = [site['id'] for site in response.json() if (site and site.get('id') and site.get('licensed'))]
        return site_ids
    else:
        raise Exception(f"Failed to fetch facility IDs for tenant {tenant_name}: {response.status_code}")



def prepare_tenant_data():
    """
    Prepares the tenant data by fetching facility and carrier IDs.
    This function should be called before generating the exhaustive CSV.
    """
    TENANT_DATA = {}
    for tenant in TENANTS_AUTH_TOKEN:
        bearer_token = TENANTS_AUTH_TOKEN[tenant]
        facility_ids = get_licensed_facility_ids_for_tenant(tenant, bearer_token)
        if not facility_ids:
            print(f"No licensed facilities found for tenant: {tenant}. Skipping...")
            continue

        carrier_ids = get_carrier_data_for_tenant(tenant, bearer_token)
        if not carrier_ids:
            print(f"No carriers found for tenant: {tenant}. Skipping...")

        TENANT_DATA[tenant] = {
            "facility_ids": facility_ids,
            "carrier_ids": carrier_ids,
            "auth_token": bearer_token
        }

    return TENANT_DATA


def generate_exhaustive_csv(filename="test_data.csv"):
    """Generates an exhaustive CSV for all API payload combinations."""
    
    all_rows = []


    tenant_data = prepare_tenant_data()
    if not tenant_data:
        print("No tenant data available. Please check your tenant configurations.")
        return
    
    
    for tenant, data in tenant_data.items():
        print(f"Generating data for tenant: {tenant}...")
        
        # Define common parameter sets
        auth_token = data["auth_token"]

        # --- Endpoints requiring only facilityId ---
        simple_endpoints = [
            "yard-availability", 
            "task-workload-summary", 
            "task-attention-summary", 
            "door-breakdown-summary"
        ]
        for endpoint in simple_endpoints:
            for facility_id in data["facility_ids"]:
                payload = json.dumps({"facilityId": facility_id})
                # add this 5 times
                for _ in range(COUNTER):
                    all_rows.append({
                        "api_endpoint": endpoint, "tenantName": tenant, "facilityId": facility_id, 
                        "authToken": auth_token, "payload": payload
                    })
                

        # --- Endpoints requiring facilityId and carrierIds ---
        carrier_endpoints = [
            "site-occupancy",
            "dwell-time-summary",
            "detention-summary"
        ]
        for endpoint in carrier_endpoints:
            for facility_id in data["facility_ids"]:
                payload = json.dumps({"facilityId": facility_id, "carrierIds": data["carrier_ids"]})
                for _ in range(COUNTER):
                    all_rows.append({
                        "api_endpoint": endpoint, "tenantName": tenant, "facilityId": facility_id, 
                        "authToken": auth_token, "payload": payload
                    })

        # --- Trailer Overview Combinations ---
        params = list(itertools.product(data["facility_ids"], TRAILER_STATES))
        for p in params:
            payload = json.dumps({"facilityId": p[0], "carrierIds": data["carrier_ids"], "trailerState": p[1]})
            all_rows.append({
                "api_endpoint": "trailer-overview", "tenantName": tenant, "facilityId": p[0],
                "authToken": auth_token, "payload": payload
            })

        # --- Trailer Exception Summary Combinations ---
        # Use only one threshold combination per facility for equal distribution
        for facility_id in data["facility_ids"]:
            payload = json.dumps({
                "facilityId": facility_id, 
                "carrierIds": data["carrier_ids"], 
                "lastDetectionTimeThresholdHours": 24,  # Use default threshold
                "inboundLoadedThresholdHours": 48       # Use default threshold
            })
            for _ in range(COUNTER):
                all_rows.append({
                    "api_endpoint": "trailer-exception-summary", "tenantName": tenant, "facilityId": facility_id,
                    "authToken": auth_token, "payload": payload
                })

        # --- Shipment Volume Forecast Combinations ---
        params = list(itertools.product(data["facility_ids"], SHIPMENT_DIRECTIONS))
        for p in params:
            payload = json.dumps({
                "facilityId": p[0],
                "carrierIds": data["carrier_ids"],
                "shipmentDirection": p[1],
                "timeZone": "GMT",
                "numDays": 7,
                "startDate": "2025-07-30",
                "includeShipmentsWithoutCarrier": True
            })
            for _ in range(2):
                all_rows.append({
                    "api_endpoint": "shipment-volume-forecast", "tenantName": tenant, "facilityId": p[0],
                    "authToken": auth_token, "payload": payload
                })

    # Write all generated rows to the CSV file
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(HEADER)
        
        for row_dict in all_rows:
            # Fill in default values for JMeter script compatibility
            row_dict.setdefault("activeUsers", 10)
            row_dict.setdefault("rpmPerUser", 60)
            row_dict.setdefault("rampUpSeconds", 1)
            # Write the row by getting values from the dictionary, ensuring correct order
            writer.writerow([row_dict.get(h, "") for h in HEADER])

    print(f"\nSuccessfully generated {len(all_rows)} exhaustive test cases in '{filename}'")

# Run the generator
generate_exhaustive_csv()