# AWS Infrastructure Deployment with Pulumi and Python

## Overview

This project uses Pulumi with Python to deploy a basic AWS infrastructure. It creates a VPC, a public subnet, an EC2 instance, and configures SSH access to the instance.

## Prerequisites

- Python 3.7 or later
- Pulumi CLI
- AWS CLI
- An AWS account with appropriate permissions

## Setup

1. Install required software:
   - [Python](https://www.python.org/downloads/)
   - [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/)
   - [AWS CLI](https://aws.amazon.com/cli/)

2. Configure AWS CLI with your credentials:
   ```
   aws configure
   ```

3. Create a new directory for the project:
   ```
   mkdir pulumi-aws-python && cd pulumi-aws-python
   ```

4. Initialize a new Pulumi project:
   ```
   pulumi new aws-python
   ```

5. Generate an SSH key pair:
   ```
   ssh-keygen -t rsa -b 2048 -f ./id_rsa_pulumi
   ```

## Project Structure

```
pulumi-aws-python/
│
├── __main__.py          # Main Pulumi program
├── requirements.txt     # Python dependencies
├── Pulumi.yaml          # Pulumi project file
├── id_rsa_pulumi        # SSH private key (do not commit to version control)
└── id_rsa_pulumi.pub    # SSH public key
```

## Code

Replace the contents of `__main__.py` with the following code:

```python
import pulumi
from pulumi_aws import ec2, get_availability_zones
import os

# Create a new VPC
vpc = ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "my-vpc"})

# Create an Internet Gateway
igw = ec2.InternetGateway("my-igw",
    vpc_id=vpc.id,
    tags={"Name": "my-igw"})

# Create a public subnet
public_subnet = ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone=get_availability_zones().names[0],
    tags={"Name": "public-subnet"})

# Create a route table
route_table = ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    routes=[ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
    )],
    tags={"Name": "public-route-table"})

# Associate the route table with the public subnet
route_table_association = ec2.RouteTableAssociation("public-route-table-association",
    subnet_id=public_subnet.id,
    route_table_id=route_table.id)

# Create a security group for SSH access
ssh_security_group = ec2.SecurityGroup("ssh-security-group",
    description="Allow SSH access",
    vpc_id=vpc.id,
    ingress=[ec2.SecurityGroupIngressArgs(
        description="SSH from anywhere",
        from_port=22,
        to_port=22,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
    )],
    egress=[ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
    )],
    tags={"Name": "ssh-security-group"})

# Get the current working directory
current_dir = os.getcwd()

# Create a new key pair
key_pair = ec2.KeyPair("my-key-pair",
    key_name="my-key-pair",
    public_key=open(os.path.join(current_dir, "id_rsa_pulumi.pub")).read())

# Create an EC2 instance
instance = ec2.Instance("my-instance",
    instance_type="t2.micro",
    ami="ami-0c55b159cbfafe1f0",  # Amazon Linux 2 AMI (HVM), SSD Volume Type
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[ssh_security_group.id],
    key_name=key_pair.key_name,
    tags={"Name": "my-instance"})

# Output the public IP of the instance
pulumi.export("instance_public_ip", instance.public_ip)

# Output a command to SSH into the instance
pulumi.export("ssh_command", pulumi.Output.concat("ssh -i ", current_dir, "/id_rsa_pulumi ec2-user@", instance.public_ip))
```

## Deployment

1. Ensure you're in the project directory.

2. Deploy the infrastructure:
   ```
   pulumi up
   ```

3. Review the proposed changes and confirm by typing 'yes'.

4. Wait for the deployment to complete. Pulumi will output the public IP of the EC2 instance and an SSH command.

## Accessing the EC2 Instance

Use the SSH command provided in the Pulumi output to connect to your EC2 instance:

```
ssh -i ./id_rsa_pulumi ec2-user@<public-ip>
```

Replace `<public-ip>` with the actual IP address provided in the output.

## Clean Up

To avoid unnecessary AWS charges, destroy the resources when they're no longer needed:

```
pulumi destroy
```

Confirm the destruction by typing 'yes'.

## Security Considerations

- The current setup allows SSH access from any IP (0.0.0.0/0). For production use, restrict this to specific IP ranges.
- Keep your AWS credentials and SSH private key secure.
- Regularly update your EC2 instance and security group rules.

## Customization

You can modify the `__main__.py` script to:
- Change instance types
- Add more security rules
- Incorporate additional AWS services

## Troubleshooting

- If you encounter "no such host" errors, try flushing your DNS cache:
  ```
  ipconfig /flushdns
  ```
- Ensure your AWS credentials are correctly configured.
- Check that all required files (including the SSH public key) are in the correct location.

## Version Control

- Add the private key (`id_rsa_pulumi`) to your `.gitignore` file to prevent accidental commits.
- Version control your Pulumi scripts for easy tracking of infrastructure changes.

## Additional Resources

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [AWS Python SDK (Boto3) Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

This documentation provides a comprehensive guide for setting up, deploying, and managing your AWS infrastructure using Pulumi with Python. It includes the full Python code for creating the infrastructure, along with sections on prerequisites, setup, project structure, deployment instructions, security considerations, and troubleshooting tips.

The code creates a VPC, a public subnet, an Internet Gateway, a route table, a security group allowing SSH access, and an EC2 instance. It also sets up an SSH key pair for accessing the instance.

Remember to customize any parts of this documentation or code as needed for your specific project requirements.