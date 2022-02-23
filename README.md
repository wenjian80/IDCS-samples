# IDCS-samples
Welcome to my collection of IDCS samples.
It includes examples of Oracle IDCS to AzureAD and IDCS to Oracle Fusion ERP integration, and audit collection with REST.
It is interlinked, any federated SSO request or user creation will create an audit record, and the audit REST API
is built on SCIM, same standard the REST APIs used fro Azure and Fusion provisioning uses.

- SSO between Oracle IDCS and Oracle Fusion  (fusion13sso_v3.pdf)
- SSO between Azure AD and IDCS (azureAD_federation_v4.pdf)
- Provisioning from AzureAD to Oracle IDCS (azureAD_provisioning_v2.pdf)
- Example of custom claims in AzureAD that mask off the Azure domain name, if the username in IDCS is without domain name (custom_claims_v1.pdf)
- How to configure MFA within IDCS (MFA_Setup.pdf)
- Shellscript that pull the audit trail, based on a standard SCIM filter

- Shell scrip that fetches the JWT BEarer token, for use with the REST API
- Python script that pulls data of the OCI audit trail. This scirp recuires OCI CLI and API key configuration
The lazy ones, just use the OCI Cloud shell, giving you a OCI CLI/SDK envrionment without any manual .oci config work

### Examples of commandlines
Pull all IDCS Audit since 2022-21-02 15:25
    sh getaudit 7550e9d8a28e41a5a5beb26fbfbfbfbfb 35b44b44-c76b-49d2-8b8b-e19c6e98c534 https://\<your IDCS URL\>.identity.oraclecloud.com '?filter=timestamp%20gt%20%222022-02-21T15:25:00.001Z%22%20'
  
Generate JWT token for API usage (like postman)
```sh gettoken 7550e9d8a28e41a5a5beb26fbfbfbfbfb 35b44b44-c76b-49d2-8b8b-e19c6e98c534 https://<your IDCS URL>.identity.oraclecloud.com
```  
Use OCI CLI to fetch Audit records
oci audit event list --compartment-id ocid1.tenancy.oc1..aaaaaaaaflf2uasr2shm5ag2yulp4gjy3aoqvwvvbcmvuk52xxxxxxxxxx \
  --start-time '2022-02-21 14:25' --end-time '2022-02-21 17:25'

Run Python script to pull OCI Audit record (Written for python 2.x)

python --configfile myconfig --starttime "2022-15-05T07:00:00" --endtime "2022-15-05T07:00:00" --outfile audit.json
The Configfile is a json file like this:
  
  {"tenantOCID":"ocid1.tenancy.oc1..aaaaaaaaflf2uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
 "userOCID":"ocid1.user.oc1..aaaaaaaaryi42cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
 "fingerPrint":"21:2b:90:a8:ec:a2:10:61:d1:41:b1:3a:93:ac:93:9b",
 "privateKeyFile":"/home/ocitest/.oci/oci_api_key.pem",
 "iaasAPIUri":"https://iaas.eu-frankfurt-1.oraclecloud.com",
 "availabilityDomainPrefix":"wTjm%3AEU-FRANKFURT-1-AD-"}
  

### Additional blogs on the topics around fusion and IDCS integration is found here.
  
[Role based Provisioning from Oracle Fusion Application to IDCS](https://blogs.oracle.com/cloud-infrastructure/post/role-based-provisioning-from-oracle-fusion-application-to-idcs-v2)
  
[Managing Users In Identity Cloud Service – Part 1](https://blogs.oracle.com/cloudsecurity/post/managing-users-in-identity-cloud-service-pt1)
  
[Managing Users In Identity Cloud Service – Part 2](https://blogs.oracle.com/cloudsecurity/post/managing-users-in-identity-cloud-service-pt2)

[OCI CLI Configuration](https://github.com/oracle/oci-cli)

### REST examples and Scripts

[gettoken, shellscript that generates a JWT token based on clientid/client secret and IDCS URL](https://github.com/bios62/IDCS-samples/blob/main/gettoken)

[getaudit, shellscript that pull audittrail based on standard SCIM filter, with on clientid/client secret and IDCS URL](https://github.com/bios62/IDCS-samples/blob/main/getaudit)

[getaudit.py, python script (python 2.x) that pulls the OCI, not IDCS, audit trail based on start/end date using OCI CLI configuration)](https://github.com/bios62/IDCS-samples/blob/main/getaudit.py)

  
  
