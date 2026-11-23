#include "ns3/traffic-control-module.h"

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"

#include <fstream>
#include <iostream>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("TcpCwndSimulation");

// Record congestion window changes
static std::ofstream cwndFile;

static void
CwndChange(uint32_t oldCwnd, uint32_t newCwnd)
{
    cwndFile << Simulator::Now().GetSeconds()
             << " " << newCwnd
             << std::endl;
}

// Connect the congestion-window trace
static void
ConnectCwndTrace()
{
    Config::ConnectWithoutContext(
        "/NodeList/0/$ns3::TcpL4Protocol/SocketList/0/CongestionWindow",
        MakeCallback(&CwndChange));
}

int main(int argc, char *argv[])
{
    // Select TCP NewReno congestion control
    Config::SetDefault(
        "ns3::TcpL4Protocol::SocketType",
        TypeIdValue(TcpNewReno::GetTypeId())
    );

    // Set TCP segment size to 1000 bytes
    Config::SetDefault(
        "ns3::TcpSocket::SegmentSize",
        UintegerValue(1000)
    );

    std::cout << "TCP NewReno Simulation" << std::endl;


    // Create four network nodes
    NodeContainer nodes;
    nodes.Create(4);

    std::string bottleneckRate = "10Mbps";
    std::string bottleneckDelay = "20ms";
    CommandLine cmd(__FILE__);
    cmd.AddValue("bottleneckRate", "Bottleneck bandwidth", bottleneckRate);
    cmd.AddValue("bottleneckDelay", "Bottleneck one-way delay", bottleneckDelay);
    cmd.Parse(argc, argv);

    // Configure fast access links
    PointToPointHelper accessLink;
    accessLink.SetDeviceAttribute(
        "DataRate", StringValue("100Mbps"));
    accessLink.SetChannelAttribute(
        "Delay", StringValue("2ms"));

    // Configure the bottleneck link
    PointToPointHelper bottleneckLink;
    bottleneckLink.SetDeviceAttribute(
        "DataRate", StringValue(bottleneckRate));
    bottleneckLink.SetChannelAttribute(
        "Delay", StringValue(bottleneckDelay));

    // Set bottleneck device queue to 50 packets
    bottleneckLink.SetQueue(
        "ns3::DropTailQueue",
        "MaxSize", StringValue("50p"));

    // Connect Sender - R1 - R2 - Receiver
    NetDeviceContainer d0d1 =
        accessLink.Install(nodes.Get(0), nodes.Get(1));

    // Disable automatic queue-disc installation

    NetDeviceContainer d1d2 =
        bottleneckLink.Install(nodes.Get(1), nodes.Get(2));

    // Remove the automatic queue disc on the bottleneck

    NetDeviceContainer d2d3 =
        accessLink.Install(nodes.Get(2), nodes.Get(3));

    std::cout << "Four-node network created successfully"
              << std::endl;


    // Install the TCP/IP Internet stack
    InternetStackHelper internet;
    internet.Install(nodes);

    // Assign IP addresses to the three links
    Ipv4AddressHelper address;

    address.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer i0i1 =
        address.Assign(d0d1);

    address.SetBase("10.1.2.0", "255.255.255.0");
    Ipv4InterfaceContainer i1i2 =
        address.Assign(d1d2);

    address.SetBase("10.1.3.0", "255.255.255.0");
    Ipv4InterfaceContainer i2i3 =
        address.Assign(d2d3);

    // Enable routing between all nodes
    Ipv4GlobalRoutingHelper::PopulateRoutingTables();

    std::cout << "Internet stack and IP addresses configured"
              << std::endl;


    // Configure TCP receiver
    uint16_t port = 50000;

    PacketSinkHelper sink(
        "ns3::TcpSocketFactory",
        InetSocketAddress(Ipv4Address::GetAny(), port));

    ApplicationContainer sinkApp =
        sink.Install(nodes.Get(3));

    sinkApp.Start(Seconds(0.0));
    sinkApp.Stop(Seconds(60.0));

    // Configure TCP sender
    BulkSendHelper source(
        "ns3::TcpSocketFactory",
        InetSocketAddress(i2i3.GetAddress(1), port));

    source.SetAttribute("MaxBytes", UintegerValue(0));

    ApplicationContainer sourceApp =
        source.Install(nodes.Get(0));

    sourceApp.Start(Seconds(1.0));
    sourceApp.Stop(Seconds(59.0));

    // Include experimental parameters in output names to avoid overwriting.
    std::string tag = bottleneckRate + "-" + bottleneckDelay;

    // Open the congestion-window data file
    cwndFile.open("newreno-" + tag + "-cwnd.dat");

    // Connect after the sender application starts
    Simulator::Schedule(
        Seconds(1.01),
        &ConnectCwndTrace);

    // Run the simulation
    // Install FlowMonitor to collect network statistics
    FlowMonitorHelper flowmonHelper;
    Ptr<FlowMonitor> flowmon = flowmonHelper.InstallAll();

    Simulator::Stop(Seconds(60.0));
    Simulator::Run();

    std::cout << "TCP data transmission completed"
              << std::endl;


    // Check how many bytes the receiver received
    Ptr<PacketSink> receiver =
        DynamicCast<PacketSink>(sinkApp.Get(0));

    std::cout << "Total received bytes: "
              << receiver->GetTotalRx()
              << std::endl;

    // Save FlowMonitor statistics before destroying the simulation
    flowmon->CheckForLostPackets();
    flowmon->SerializeToXmlFile("newreno-" + tag + "-flowmon.xml", true, true);

    Simulator::Destroy();

    return 0;
}
