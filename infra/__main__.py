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
    ami="ami-060e277c0d4cce553",  # Ubuntu Server AMI (HVM), SSD Volume Type
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[ssh_security_group.id],
    key_name=key_pair.key_name,
    tags={"Name": "my-instance"})

# Output the public IP of the instance
pulumi.export("instance_public_ip", instance.public_ip)

# Output a command to SSH into the instance

pulumi.export("ssh_command", pulumi.Output.concat("ssh -i ", current_dir, "/id_rsa_pulumi ubuntu@", instance.public_ip))