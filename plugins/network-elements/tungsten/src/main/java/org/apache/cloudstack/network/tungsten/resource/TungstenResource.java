// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.
package org.apache.cloudstack.network.tungsten.resource;

import com.cloud.agent.IAgentControl;
import com.cloud.agent.api.Answer;
import com.cloud.agent.api.Command;
import com.cloud.agent.api.MaintainAnswer;
import com.cloud.agent.api.MaintainCommand;
import com.cloud.agent.api.PingCommand;
import com.cloud.agent.api.ReadyAnswer;
import com.cloud.agent.api.ReadyCommand;
import com.cloud.agent.api.StartupCommand;
import com.cloud.host.Host;
import com.cloud.resource.ServerResource;
import com.cloud.utils.TungstenUtils;
import net.juniper.tungsten.api.ApiConnectorFactory;
import net.juniper.tungsten.api.ApiObjectBase;
import net.juniper.tungsten.api.ApiPropertyBase;
import net.juniper.tungsten.api.ObjectReference;
import net.juniper.tungsten.api.types.FloatingIp;
import net.juniper.tungsten.api.types.FloatingIpPool;
import net.juniper.tungsten.api.types.InstanceIp;
import net.juniper.tungsten.api.types.Loadbalancer;
import net.juniper.tungsten.api.types.LoadbalancerHealthmonitor;
import net.juniper.tungsten.api.types.LoadbalancerListener;
import net.juniper.tungsten.api.types.LoadbalancerMember;
import net.juniper.tungsten.api.types.LoadbalancerPool;
import net.juniper.tungsten.api.types.LogicalRouter;
import net.juniper.tungsten.api.types.NetworkPolicy;
import net.juniper.tungsten.api.types.Project;
import net.juniper.tungsten.api.types.SequenceType;
import net.juniper.tungsten.api.types.VirtualMachine;
import net.juniper.tungsten.api.types.VirtualMachineInterface;
import net.juniper.tungsten.api.types.VirtualNetwork;
import net.juniper.tungsten.api.types.VirtualNetworkPolicyType;
import org.apache.cloudstack.api.ServerApiException;
import org.apache.cloudstack.network.tungsten.agent.api.AddTungstenNetworkSubnetCommand;
import org.apache.cloudstack.network.tungsten.agent.api.ApplyTungstenNetworkPolicyCommand;
import org.apache.cloudstack.network.tungsten.agent.api.ApplyTungstenPortForwardingCommand;
import org.apache.cloudstack.network.tungsten.agent.api.AssignTungstenFloatingIpCommand;
import org.apache.cloudstack.network.tungsten.agent.api.ClearTungstenNetworkGatewayCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenDomainCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenFloatingIpCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenFloatingIpPoolCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenLogicalRouterCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenNetworkCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenNetworkLoadbalancerCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenNetworkPolicyCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenProjectCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenVirtualMachineCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenDomainCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenFloatingIpCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenFloatingIpPoolCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenLoadBalancerCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenLoadBalancerListenerCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenNetworkCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenNetworkPolicyCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenObjectCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenProjectCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenVRouterPortCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenVmCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenVmInterfaceCommand;
import org.apache.cloudstack.network.tungsten.agent.api.GetTungstenFabricNetworkCommand;
import org.apache.cloudstack.network.tungsten.agent.api.GetTungstenFloatingIpsCommand;
import org.apache.cloudstack.network.tungsten.agent.api.GetTungstenLoadBalancerCommand;
import org.apache.cloudstack.network.tungsten.agent.api.GetTungstenNatIpCommand;
import org.apache.cloudstack.network.tungsten.agent.api.GetTungstenNetworkCommand;
import org.apache.cloudstack.network.tungsten.agent.api.ReleaseTungstenFloatingIpCommand;
import org.apache.cloudstack.network.tungsten.agent.api.RemoveTungstenNetworkSubnetCommand;
import org.apache.cloudstack.network.tungsten.agent.api.SetTungstenNetworkGatewayCommand;
import org.apache.cloudstack.network.tungsten.agent.api.StartupTungstenCommand;
import org.apache.cloudstack.network.tungsten.agent.api.TungstenAnswer;
import org.apache.cloudstack.network.tungsten.agent.api.UpdateLoadBalancerServiceInstanceCommand;
import org.apache.cloudstack.network.tungsten.agent.api.UpdateTungstenLoadBalancerListenerCommand;
import org.apache.cloudstack.network.tungsten.agent.api.UpdateTungstenLoadBalancerMemberCommand;
import org.apache.cloudstack.network.tungsten.agent.api.UpdateTungstenLoadBalancerPoolCommand;
import org.apache.cloudstack.network.tungsten.model.TungstenLoadBalancerMember;
import org.apache.cloudstack.network.tungsten.service.TungstenApi;
import org.apache.cloudstack.network.tungsten.service.TungstenVRouterApi;
import org.apache.cloudstack.network.tungsten.vrouter.Port;
import org.apache.cloudstack.network.tungsten.vrouter.Subnet;
import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import javax.naming.ConfigurationException;

public class TungstenResource implements ServerResource {

    private static final Logger s_logger = Logger.getLogger(TungstenResource.class);

    private String _name;
    private String _guid;
    private String _zoneId;
    private int _numRetries;
    private String _hostname;
    private String _port;
    private String _vrouterPort;
    private String _introspectPort;

    private TungstenApi _tungstenApi;

    @Override
    public boolean configure(String name, Map<String, Object> params) throws ConfigurationException {

        _name = (String) params.get("name");
        if (_name == null) {
            throw new ConfigurationException("Unable to find name");
        }

        _guid = (String) params.get("guid");
        if (_guid == null) {
            throw new ConfigurationException("Unable to find the guid");
        }

        _zoneId = (String) params.get("zoneId");
        if (_zoneId == null) {
            throw new ConfigurationException("Unable to find zone");
        }

        _numRetries = 2;

        _hostname = (String) params.get("hostname");
        if (_hostname == null) {
            throw new ConfigurationException("Missing tungsten hostname from params: " + params);
        }

        _port = (String) params.get("port");
        if (_port == null) {
            throw new ConfigurationException("Missing tungsten port from params: " + params);
        }

        _vrouterPort = (String) params.get("vrouterPort");
        if (_vrouterPort == null) {
            throw new ConfigurationException("Missing tungsten vrouter port from params: " + params);
        }

        _introspectPort = (String) params.get("introspectPort");
        if (_introspectPort == null) {
            throw new ConfigurationException("Missing tungsten introspect port from params: " + params);
        }

        _tungstenApi = new TungstenApi();
        _tungstenApi.setHostname(_hostname);
        _tungstenApi.setPort(_port);
        _tungstenApi.setApiConnector(ApiConnectorFactory.build(_hostname, Integer.parseInt(_port)));
        return true;
    }

    @Override
    public Host.Type getType() {
        return Host.Type.L2Networking;
    }

    @Override
    public String getName() {
        return _name;
    }

    @Override
    public StartupCommand[] initialize() {
        StartupTungstenCommand sc = new StartupTungstenCommand();
        sc.setGuid(_guid);
        sc.setName(_name);
        sc.setDataCenter(_zoneId);
        sc.setPod("");
        sc.setPrivateIpAddress("");
        sc.setStorageIpAddress("");
        sc.setVersion("");
        return new StartupCommand[] {sc};
    }

    @Override
    public PingCommand getCurrentStatus(long id) {
        try {
            _tungstenApi.checkTungstenProviderConnection();
        } catch (ServerApiException e) {
            s_logger.error("Check tungsten provider connection failed", e);
            return null;
        }
        return new PingCommand(Host.Type.L2Networking, id);
    }

    @Override
    public Answer executeRequest(Command cmd) {
        return executeRequest(cmd, _numRetries);
    }

    public Answer executeRequest(Command cmd, int numRetries) {
        if (cmd instanceof ReadyCommand) {
            return executeRequest((ReadyCommand) cmd);
        } else if (cmd instanceof MaintainCommand) {
            return executeRequest((MaintainCommand) cmd);
        } else if (cmd instanceof CreateTungstenNetworkCommand) {
            return executeRequest((CreateTungstenNetworkCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenNetworkCommand) {
            return executeRequest((DeleteTungstenNetworkCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenVmInterfaceCommand) {
            return executeRequest((DeleteTungstenVmInterfaceCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenVmCommand) {
            return executeRequest((DeleteTungstenVmCommand) cmd, numRetries);
        } else if (cmd instanceof CreateTungstenLogicalRouterCommand) {
            return executeRequest((CreateTungstenLogicalRouterCommand) cmd, numRetries);
        } else if (cmd instanceof CreateTungstenVirtualMachineCommand) {
            return executeRequest((CreateTungstenVirtualMachineCommand) cmd, numRetries);
        } else if (cmd instanceof SetTungstenNetworkGatewayCommand) {
            return executeRequest((SetTungstenNetworkGatewayCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenVRouterPortCommand) {
            return executeRequest((DeleteTungstenVRouterPortCommand) cmd, numRetries);
        } else if (cmd instanceof GetTungstenNetworkCommand) {
            return executeRequest((GetTungstenNetworkCommand) cmd, numRetries);
        } else if (cmd instanceof ClearTungstenNetworkGatewayCommand) {
            return executeRequest((ClearTungstenNetworkGatewayCommand) cmd, numRetries);
        } else if (cmd instanceof CreateTungstenFloatingIpPoolCommand) {
            return executeRequest((CreateTungstenFloatingIpPoolCommand) cmd, numRetries);
        } else if (cmd instanceof CreateTungstenFloatingIpCommand) {
            return executeRequest((CreateTungstenFloatingIpCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenFloatingIpCommand) {
            return executeRequest((DeleteTungstenFloatingIpCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenFloatingIpPoolCommand) {
            return executeRequest((DeleteTungstenFloatingIpPoolCommand) cmd, numRetries);
        } else if (cmd instanceof AssignTungstenFloatingIpCommand) {
            return executeRequest((AssignTungstenFloatingIpCommand) cmd, numRetries);
        } else if (cmd instanceof ReleaseTungstenFloatingIpCommand) {
            return executeRequest((ReleaseTungstenFloatingIpCommand) cmd, numRetries);
        } else if (cmd instanceof GetTungstenNatIpCommand) {
            return executeRequest((GetTungstenNatIpCommand) cmd, numRetries);
        } else if (cmd instanceof CreateTungstenNetworkPolicyCommand) {
            return executeRequest((CreateTungstenNetworkPolicyCommand) cmd, numRetries);
        } else if (cmd instanceof ApplyTungstenNetworkPolicyCommand) {
            return executeRequest((ApplyTungstenNetworkPolicyCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenNetworkPolicyCommand) {
            return executeRequest((DeleteTungstenNetworkPolicyCommand) cmd, numRetries);
        } else if (cmd instanceof GetTungstenFloatingIpsCommand) {
            return executeRequest((GetTungstenFloatingIpsCommand) cmd, numRetries);
        } else if (cmd instanceof GetTungstenFabricNetworkCommand) {
            return executeRequest((GetTungstenFabricNetworkCommand) cmd, numRetries);
        } else if (cmd instanceof CreateTungstenNetworkLoadbalancerCommand) {
            return executeRequest((CreateTungstenNetworkLoadbalancerCommand) cmd, numRetries);
        } else if (cmd instanceof UpdateLoadBalancerServiceInstanceCommand) {
            return executeRequest((UpdateLoadBalancerServiceInstanceCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenLoadBalancerCommand) {
            return executeRequest((DeleteTungstenLoadBalancerCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenLoadBalancerListenerCommand) {
            return executeRequest((DeleteTungstenLoadBalancerListenerCommand) cmd, numRetries);
        } else if (cmd instanceof UpdateTungstenLoadBalancerPoolCommand) {
            return executeRequest((UpdateTungstenLoadBalancerPoolCommand) cmd, numRetries);
        } else if (cmd instanceof UpdateTungstenLoadBalancerMemberCommand) {
            return executeRequest((UpdateTungstenLoadBalancerMemberCommand) cmd, numRetries);
        } else if (cmd instanceof UpdateTungstenLoadBalancerListenerCommand) {
            return executeRequest((UpdateTungstenLoadBalancerListenerCommand) cmd, numRetries);
        } else if (cmd instanceof GetTungstenLoadBalancerCommand) {
            return executeRequest((GetTungstenLoadBalancerCommand) cmd, numRetries);
        } else if (cmd instanceof CreateTungstenDomainCommand) {
            return executeRequest((CreateTungstenDomainCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenDomainCommand) {
            return executeRequest((DeleteTungstenDomainCommand) cmd, numRetries);
        } else if (cmd instanceof CreateTungstenProjectCommand) {
            return executeRequest((CreateTungstenProjectCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenProjectCommand) {
            return executeRequest((DeleteTungstenProjectCommand) cmd, numRetries);
        } else if (cmd instanceof ApplyTungstenPortForwardingCommand) {
            return executeRequest((ApplyTungstenPortForwardingCommand) cmd, numRetries);
        } else if (cmd instanceof DeleteTungstenObjectCommand) {
            return executeRequest((DeleteTungstenObjectCommand) cmd, numRetries);
        } else if (cmd instanceof AddTungstenNetworkSubnetCommand) {
            return executeRequest((AddTungstenNetworkSubnetCommand) cmd, numRetries);
        } else if (cmd instanceof RemoveTungstenNetworkSubnetCommand) {
            return executeRequest((RemoveTungstenNetworkSubnetCommand) cmd, numRetries);
        }

        s_logger.debug("Received unsupported command " + cmd.toString());
        return Answer.createUnsupportedCommandAnswer(cmd);
    }

    private Answer executeRequest(CreateTungstenNetworkCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        if (project == null) {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }

        VirtualNetwork virtualNetwork = _tungstenApi.createTungstenNetwork(cmd.getUuid(), cmd.getName(),
            cmd.getDisplayName(), project.getUuid(), cmd.isRouterExternal(), cmd.isShared(), cmd.getIpPrefix(),
            cmd.getIpPrefixLen(), cmd.getGateway(), cmd.isDhcpEnable(), cmd.getDnsServer(), cmd.getAllocationStart(),
            cmd.getAllocationEnd(), cmd.isIpFromStart(), cmd.isManagementNetwork(), cmd.getSubnetName());

        if (virtualNetwork != null)
            return new TungstenAnswer(cmd, virtualNetwork, true, "Tungsten network created");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(DeleteTungstenVmInterfaceCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        VirtualMachineInterface vmi = (VirtualMachineInterface) _tungstenApi.getTungstenObjectByName(
            VirtualMachineInterface.class, project.getQualifiedName(), cmd.getName());
        boolean deleted = _tungstenApi.deleteTungstenVmInterface(vmi);
        if (deleted)
            return new TungstenAnswer(cmd, true, "Tungsten virtual machine interface deleted");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(DeleteTungstenVmCommand cmd, int numRetries) {
        VirtualMachine virtualMachine = (VirtualMachine) _tungstenApi.getTungstenObject(VirtualMachine.class,
            cmd.getVirtualMachineUuid());
        boolean deleted = _tungstenApi.deleteTungstenVm(virtualMachine);
        if (deleted)
            return new TungstenAnswer(cmd, true, "Tungsten virtual machine deleted");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(DeleteTungstenNetworkCommand cmd, int numRetries) {
        VirtualNetwork virtualNetwork = (VirtualNetwork) _tungstenApi.getTungstenObject(VirtualNetwork.class,
            cmd.getNetworkUuid());
        if (virtualNetwork != null) {
            boolean deleted = _tungstenApi.deleteTungstenNetwork(virtualNetwork);
            if (deleted)
                return new TungstenAnswer(cmd, true, "Tungsten network deleted");
            else {
                if (numRetries > 0) {
                    return retry(cmd, --numRetries);
                } else {
                    return new TungstenAnswer(cmd, new IOException());
                }
            }
        }
        return new TungstenAnswer(cmd, true, "Tungsten network is not exist");
    }

    private Answer executeRequest(CreateTungstenLogicalRouterCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        LogicalRouter logicalRouter = (LogicalRouter) _tungstenApi.createTungstenLogicalRouter(cmd.getName(),
            project.getUuid(), cmd.getPubNetworkUuid());
        if (logicalRouter != null)
            return new TungstenAnswer(cmd, logicalRouter, true, "Tungsten logical router created");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(CreateTungstenVirtualMachineCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        if (project == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        VirtualNetwork virtualNetwork = (VirtualNetwork) _tungstenApi.getTungstenObject(VirtualNetwork.class,
            cmd.getVnUuid());
        if (virtualNetwork == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        VirtualMachine virtualMachine = (VirtualMachine) _tungstenApi.getTungstenObject(VirtualMachine.class,
            cmd.getVmUuid());
        if (virtualMachine == null) {
            virtualMachine = _tungstenApi.createTungstenVirtualMachine(cmd.getVmUuid(), cmd.getVmName());
        }
        if (virtualMachine == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        String vmiName = TungstenUtils.getVmiName(cmd.getTrafficType(), cmd.getVmType(), cmd.getVmName(),
            cmd.getNicId());
        VirtualMachineInterface virtualMachineInterface =
            (VirtualMachineInterface) _tungstenApi.getTungstenObjectByName(
            VirtualMachineInterface.class, project.getQualifiedName(), vmiName);
        if (virtualMachineInterface == null) {
            virtualMachineInterface = _tungstenApi.createTungstenVmInterface(cmd.getNicUuid(), vmiName, cmd.getMac(),
                cmd.getVnUuid(), cmd.getVmUuid(), project.getUuid());
        }
        if (virtualMachineInterface == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        String iiName = TungstenUtils.getInstanceIpName(cmd.getTrafficType(), cmd.getVmType(), cmd.getVmName(),
            cmd.getNicId());
        InstanceIp instanceIp = (InstanceIp) _tungstenApi.getTungstenObjectByName(InstanceIp.class, null, iiName);
        if (instanceIp == null) {
            instanceIp = _tungstenApi.createTungstenInstanceIp(iiName, cmd.getIp(), cmd.getVnUuid(),
                virtualMachineInterface.getUuid());
        }
        if (instanceIp == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        Port port = new Port();
        port.setId(virtualMachineInterface.getUuid());
        port.setVnId(virtualNetwork.getUuid());
        port.setDisplayName(virtualMachine.getName());
        port.setVmProjectId(project.getUuid());
        port.setMacAddress(cmd.getMac());
        port.setIpAddress(cmd.getIp());
        port.setInstanceId(virtualMachine.getUuid());
        port.setTapInterfaceName(TungstenUtils.getTapName(cmd.getMac()));
        boolean addPortResult = TungstenVRouterApi.addTungstenVrouterPort(cmd.getHost(), _vrouterPort, port);
        if (!addPortResult) {
            return new TungstenAnswer(cmd, new IOException());
        }

        return new TungstenAnswer(cmd, virtualMachine, true, null);
    }

    private Answer executeRequest(SetTungstenNetworkGatewayCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        if (project == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        LogicalRouter logicalRouter = (LogicalRouter) _tungstenApi.getTungstenObjectByName(LogicalRouter.class,
            project.getQualifiedName(), cmd.getRouterName());
        if (logicalRouter == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        VirtualMachineInterface virtualMachineInterface =
            (VirtualMachineInterface) _tungstenApi.getTungstenObjectByName(
            VirtualMachineInterface.class, project.getQualifiedName(),
            TungstenUtils.getNetworkGatewayVmiName(cmd.getVnId()));
        if (virtualMachineInterface == null) {
            virtualMachineInterface = (VirtualMachineInterface) _tungstenApi.createTungstenGatewayVmi(
                TungstenUtils.getNetworkGatewayVmiName(cmd.getVnId()), project.getUuid(), cmd.getVnUuid());
        }
        if (virtualMachineInterface == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        InstanceIp instanceIp = (InstanceIp) _tungstenApi.getTungstenObjectByName(InstanceIp.class, null,
            TungstenUtils.getNetworkGatewayIiName(cmd.getVnId()));
        if (instanceIp == null) {
            instanceIp = _tungstenApi.createTungstenInstanceIp(TungstenUtils.getNetworkGatewayIiName(cmd.getVnId()),
                cmd.getVnGatewayIp(), cmd.getVnUuid(), virtualMachineInterface.getUuid());
        }
        if (instanceIp == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        logicalRouter.addVirtualMachineInterface(virtualMachineInterface);
        boolean updateLRResult = _tungstenApi.updateTungstenObject(logicalRouter);
        if (!updateLRResult) {
            return new TungstenAnswer(cmd, new IOException());
        }

        return new TungstenAnswer(cmd, virtualMachineInterface, true, null);
    }

    private Answer executeRequest(GetTungstenNetworkCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        if (project == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        ApiObjectBase apiObjectBase = _tungstenApi.getTungstenObjectByName(VirtualNetwork.class,
            project.getQualifiedName(), cmd.getName());
        return new TungstenAnswer(cmd, apiObjectBase, true, null);
    }

    private Answer executeRequest(ClearTungstenNetworkGatewayCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        if (project == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        LogicalRouter logicalRouter = (LogicalRouter) _tungstenApi.getTungstenObjectByName(LogicalRouter.class,
            project.getQualifiedName(), cmd.getRouterName());
        if (logicalRouter == null) {
            return new TungstenAnswer(cmd, true, null);
        }

        boolean deleteLRResult = _tungstenApi.deleteTungstenLogicalRouter(logicalRouter);
        if (!deleteLRResult) {
            return new TungstenAnswer(cmd, new IOException());
        }

        VirtualMachineInterface virtualMachineInterface =
            (VirtualMachineInterface) _tungstenApi.getTungstenObjectByName(
            VirtualMachineInterface.class, project.getQualifiedName(),
            TungstenUtils.getNetworkGatewayVmiName(cmd.getVnId()));

        if (virtualMachineInterface != null) {
            boolean deleteVmi = _tungstenApi.deleteTungstenVmInterface(virtualMachineInterface);
            if (!deleteVmi) {
                return new TungstenAnswer(cmd, new IOException());
            }
        }

        return new TungstenAnswer(cmd, true, null);
    }

    private Answer executeRequest(CreateTungstenFloatingIpPoolCommand cmd, int numRetries) {
        ApiObjectBase apiObjectBase = _tungstenApi.createTungstenFloatingIpPool(cmd.getNetworkUuid(), cmd.getFipName());
        if (apiObjectBase != null) {
            return new TungstenAnswer(cmd, apiObjectBase, true, null);
        } else {
            return new TungstenAnswer(cmd, new IOException());
        }
    }

    private Answer executeRequest(CreateTungstenFloatingIpCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        if (project == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        ApiObjectBase apiObjectBase = _tungstenApi.createTungstenFloatingIp(project.getUuid(), cmd.getNetworkUuid(),
            cmd.getFipName(), cmd.getName(), cmd.getPublicIp());
        if (apiObjectBase != null) {
            return new TungstenAnswer(cmd, apiObjectBase, true, null);
        } else {
            return new TungstenAnswer(cmd, new IOException());
        }
    }

    private Answer executeRequest(AssignTungstenFloatingIpCommand cmd, int numRetries) {
        boolean result = _tungstenApi.assignTungstenFloatingIp(cmd.getNetworkUuid(), cmd.getVmiUuid(), cmd.getFipName(),
            cmd.getName(), cmd.getPrivateIp());
        if (result) {
            return new TungstenAnswer(cmd, true, null);
        } else {
            return new TungstenAnswer(cmd, new IOException());
        }
    }

    private Answer executeRequest(ReleaseTungstenFloatingIpCommand cmd, int numRetries) {
        boolean result = _tungstenApi.releaseTungstenFloatingIp(cmd.getVnUuid(), cmd.getFipName(), cmd.getName());
        if (result) {
            return new TungstenAnswer(cmd, true, null);
        } else {
            return new TungstenAnswer(cmd, new IOException());
        }
    }

    private Answer executeRequest(GetTungstenNatIpCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        String natIp = _tungstenApi.getTungstenNatIp(project.getUuid(), cmd.getLogicalRouterUuid());
        if (natIp != null) {
            return new TungstenAnswer(cmd, true, natIp);
        } else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(DeleteTungstenVRouterPortCommand cmd, int numRetries) {
        boolean deletePort = TungstenVRouterApi.deleteTungstenVrouterPort(cmd.getHost(), _vrouterPort, cmd.getPortId());
        return new TungstenAnswer(cmd, deletePort, null);
    }

    private Answer executeRequest(DeleteTungstenFloatingIpCommand cmd, int numRetries) {
        VirtualNetwork virtualNetwork = (VirtualNetwork) _tungstenApi.getTungstenObject(VirtualNetwork.class,
            cmd.getVnUuid());
        FloatingIpPool floatingIpPool = (FloatingIpPool) _tungstenApi.getTungstenObjectByName(FloatingIpPool.class,
            virtualNetwork.getQualifiedName(), cmd.getFipName());
        FloatingIp floatingIp = (FloatingIp) _tungstenApi.getTungstenObjectByName(FloatingIp.class,
            floatingIpPool.getQualifiedName(), cmd.getName());
        boolean deleteFip = _tungstenApi.deleteTungstenFloatingIp(floatingIp);
        return new TungstenAnswer(cmd, deleteFip, null);
    }

    private Answer executeRequest(DeleteTungstenFloatingIpPoolCommand cmd, int numRetries) {
        boolean deleteFip = true;
        VirtualNetwork virtualNetwork = (VirtualNetwork) _tungstenApi.getTungstenObject(VirtualNetwork.class,
            cmd.getVnUuid());
        if (virtualNetwork != null) {
            FloatingIpPool floatingIpPool = (FloatingIpPool) _tungstenApi.getTungstenObjectByName(FloatingIpPool.class,
                virtualNetwork.getQualifiedName(), cmd.getFipName());
            if (floatingIpPool != null) {
                deleteFip = _tungstenApi.deleteTungstenFloatingIpPool(floatingIpPool);
            }
        }
        return new TungstenAnswer(cmd, deleteFip, null);
    }

    private Answer executeRequest(CreateTungstenNetworkPolicyCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        ApiObjectBase apiObjectBase = _tungstenApi.createTungstenNetworkPolicy(cmd.getName(), project.getUuid(),
            cmd.getTungstenRuleList());
        if (apiObjectBase != null) {
            return new TungstenAnswer(cmd, apiObjectBase, true, null);
        } else {
            return new TungstenAnswer(cmd, false, null);
        }
    }

    private Answer executeRequest(DeleteTungstenNetworkPolicyCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        VirtualNetwork virtualNetwork = (VirtualNetwork) _tungstenApi.getTungstenObject(VirtualNetwork.class,
            cmd.getNetworkUuid());
        NetworkPolicy networkPolicy = (NetworkPolicy) _tungstenApi.getTungstenObjectByName(NetworkPolicy.class,
            project.getQualifiedName(), cmd.getName());
        if (networkPolicy != null) {
            virtualNetwork.removeNetworkPolicy(networkPolicy, new VirtualNetworkPolicyType(new SequenceType(-1, -1)));
            boolean updated = _tungstenApi.updateTungstenObject(virtualNetwork);
            if (!updated) {
                if (numRetries > 0) {
                    return retry(cmd, --numRetries);
                } else {
                    return new TungstenAnswer(cmd, new IOException());
                }
            }

            boolean deleted = _tungstenApi.deleteTungstenNetworkPolicy(networkPolicy);
            if (deleted)
                return new TungstenAnswer(cmd, true, "Tungsten network policy deleted");
            else {
                if (numRetries > 0) {
                    return retry(cmd, --numRetries);
                } else {
                    return new TungstenAnswer(cmd, new IOException());
                }
            }
        }
        return new TungstenAnswer(cmd, true, "Tungsten network policy is not exist");
    }

    private Answer executeRequest(GetTungstenFloatingIpsCommand cmd, int numRetries) {
        VirtualNetwork virtualNetwork = (VirtualNetwork) _tungstenApi.getTungstenObject(VirtualNetwork.class,
            cmd.getVnUuid());
        List<FloatingIp> floatingIpList;
        if (virtualNetwork != null) {
            FloatingIpPool floatingIpPool = (FloatingIpPool) _tungstenApi.getTungstenObjectByName(FloatingIpPool.class,
                virtualNetwork.getQualifiedName(), cmd.getFipName());
            floatingIpList = (List<FloatingIp>) _tungstenApi.getTungstenListObject(FloatingIp.class, floatingIpPool);
        } else {
            floatingIpList = new ArrayList<>();
        }
        return new TungstenAnswer(cmd, floatingIpList, true, null);
    }

    private Answer executeRequest(ApplyTungstenNetworkPolicyCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        boolean result = _tungstenApi.applyTungstenNetworkPolicy(project.getUuid(), cmd.getNetworkPolicyName(),
            cmd.getNetworkUuid(), cmd.isPriority());
        return new TungstenAnswer(cmd, result, null);
    }

    private Answer executeRequest(GetTungstenFabricNetworkCommand cmd, int numRetries) {
        ApiObjectBase fabricNetwork = _tungstenApi.getTungstenFabricNetwork();
        if (fabricNetwork != null) {
            return new TungstenAnswer(cmd, fabricNetwork, true, null);
        } else {
            return new TungstenAnswer(cmd, false, "tungsten fabric network doesn't exist");
        }
    }

    private Answer executeRequest(CreateTungstenDomainCommand cmd, int numRetries) {
        ApiObjectBase tungstenDomain = _tungstenApi.createTungstenDomain(cmd.getTungstenDomainName(),
            cmd.getTungstenDomainUuid());
        if (tungstenDomain != null) {
            return new TungstenAnswer(cmd, tungstenDomain, true, null);
        } else {
            return new TungstenAnswer(cmd, false, null);
        }
    }

    private Answer executeRequest(CreateTungstenProjectCommand cmd, int numRetries) {
        ApiObjectBase tungstenProject = _tungstenApi.createTungstenProject(cmd.getTungstenProjectName(),
            cmd.getTungstenProjectUuid(), cmd.getTungstenDomainUuid(), cmd.getTungstenDomainName());
        if (tungstenProject != null) {
            return new TungstenAnswer(cmd, tungstenProject, true, null);
        } else {
            return new TungstenAnswer(cmd, false, null);
        }
    }

    private Answer executeRequest(DeleteTungstenDomainCommand cmd, int numRetries) {
        boolean deleted = _tungstenApi.deleteTungstenDomain(cmd.getTungstenDomainUuid());
        if (deleted) {
            return new TungstenAnswer(cmd, true, "Tungsten domain deleted");
        } else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(DeleteTungstenProjectCommand cmd, int numRetries) {
        boolean deleted = _tungstenApi.deleteTungstenProject(cmd.getTungstenProjectUuid());
        if (deleted) {
            return new TungstenAnswer(cmd, true, "Tungsten project deleted");
        } else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(CreateTungstenNetworkLoadbalancerCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        if (project == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        VirtualNetwork virtualNetwork = (VirtualNetwork) _tungstenApi.getTungstenObject(VirtualNetwork.class,
            cmd.getNetworkUuid());
        if (virtualNetwork == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        String subnetUuid = _tungstenApi.getSubnetUuid(cmd.getNetworkUuid());
        if (subnetUuid == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        // create loadbalancer vmi
        VirtualMachineInterface virtualMachineInterface =
            (VirtualMachineInterface) _tungstenApi.getTungstenObjectByName(
            VirtualMachineInterface.class, project.getQualifiedName(), cmd.getLoadBalancerVmiName());
        if (virtualMachineInterface == null) {
            virtualMachineInterface = (VirtualMachineInterface) _tungstenApi.createTungstenLbVmi(
                cmd.getLoadBalancerVmiName(), project.getUuid(), virtualNetwork.getUuid());
        }

        if (virtualMachineInterface == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        // create loadbalancer ii
        InstanceIp instanceIp = (InstanceIp) _tungstenApi.getTungstenObjectByName(InstanceIp.class, null,
            cmd.getLoadBalancerIiName());
        if (instanceIp == null) {
            instanceIp = _tungstenApi.createTungstenInstanceIp(cmd.getLoadBalancerIiName(), cmd.getPrivateIp(),
                cmd.getNetworkUuid(), virtualMachineInterface.getUuid(), subnetUuid);
        }
        if (instanceIp == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        // update loadbalancer floating ip
        // must not source nat ip or static nat ip
        // UI : don't allow add loadbalancer on source nat & static nat ip
        // check this on tungsten create load balance rule
        boolean result = _tungstenApi.assignTungstenFloatingIp(cmd.getPublicNetworkUuid(),
            virtualMachineInterface.getUuid(), cmd.getFipName(), cmd.getFiName(), cmd.getPrivateIp());
        if (!result) {
            return new TungstenAnswer(cmd, new IOException());
        }

        Loadbalancer loadbalancer = (Loadbalancer) _tungstenApi.getTungstenObjectByName(Loadbalancer.class,
            project.getQualifiedName(), cmd.getLoadBalancerName());
        if (loadbalancer == null) {
            loadbalancer = (Loadbalancer) _tungstenApi.createTungstenLoadbalancer(project.getUuid(),
                cmd.getLoadBalancerName(), virtualMachineInterface.getUuid(), subnetUuid, cmd.getPrivateIp());
        }

        if (loadbalancer == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        LoadbalancerListener loadbalancerListener = (LoadbalancerListener) _tungstenApi.getTungstenObjectByName(
            LoadbalancerListener.class, project.getQualifiedName(), cmd.getLoadBalancerListenerName());
        if (loadbalancerListener == null) {
            loadbalancerListener = (LoadbalancerListener) _tungstenApi.createTungstenLoadbalancerListener(
                project.getUuid(), loadbalancer.getUuid(), cmd.getLoadBalancerListenerName(), cmd.getProtocol(),
                cmd.getSrcPort());
        }

        if (loadbalancerListener == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        LoadbalancerHealthmonitor loadbalancerHealthmonitor =
            (LoadbalancerHealthmonitor) _tungstenApi.getTungstenObjectByName(
            LoadbalancerHealthmonitor.class, project.getQualifiedName(), cmd.getLoadBalancerHealthMonitorName());
        if (loadbalancerHealthmonitor == null) {
            loadbalancerHealthmonitor =
                (LoadbalancerHealthmonitor) _tungstenApi.createTungstenLoadbalancerHealthMonitor(
                project.getUuid(), cmd.getLoadBalancerHealthMonitorName(), cmd.getMonitorType(), cmd.getMaxRetries(),
                cmd.getDelay(), cmd.getTimeout(), cmd.getHttpMethod(), cmd.getUrlPath(), cmd.getExpectedCodes());
        }

        if (loadbalancerHealthmonitor == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        LoadbalancerPool loadbalancerPool = (LoadbalancerPool) _tungstenApi.getTungstenObjectByName(
            LoadbalancerPool.class, project.getQualifiedName(), cmd.getLoadBalancerPoolName());

        if (loadbalancerPool == null) {
            loadbalancerPool = (LoadbalancerPool) _tungstenApi.createTungstenLoadbalancerPool(project.getUuid(),
                loadbalancerListener.getUuid(), loadbalancerHealthmonitor.getUuid(), cmd.getLoadBalancerPoolName(),
                cmd.getLoadBalancerMethod(), cmd.getProtocol());
        }

        if (loadbalancerPool == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        for (TungstenLoadBalancerMember member : cmd.getListMember()) {
            LoadbalancerMember loadbalancerMember = (LoadbalancerMember) _tungstenApi.getTungstenObjectByName(
                LoadbalancerMember.class, loadbalancerPool.getQualifiedName(), member.getName());
            if (loadbalancerMember == null) {
                loadbalancerMember = (LoadbalancerMember) _tungstenApi.createTungstenLoadbalancerMember(
                    loadbalancerPool.getUuid(), member.getName(), member.getIpAddress(), subnetUuid, member.getPort(),
                    member.getWeight());
            }

            if (loadbalancerMember == null) {
                return new TungstenAnswer(cmd, new IOException());
            }
        }

        return new TungstenAnswer(cmd, loadbalancer, true, null);
    }

    private Answer executeRequest(UpdateLoadBalancerServiceInstanceCommand cmd, int numRetries) {
        boolean result = _tungstenApi.updateLBServiceInstanceFatFlow(cmd.getPublicNetworkUuid(),
            cmd.getFloatingPoolName(), cmd.getFloatingIpName());

        if (result) {
            return new TungstenAnswer(cmd, true, null);
        } else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(DeleteTungstenLoadBalancerCommand cmd, int numRetries) {
        boolean result = true;
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        Loadbalancer loadbalancer = (Loadbalancer) _tungstenApi.getTungstenObjectByName(Loadbalancer.class,
            project.getQualifiedName(), cmd.getLoadBalancerName());
        if (loadbalancer != null) {
            // delete load balancer listener
            List<ObjectReference<ApiPropertyBase>> listLoadBalancerListener =
                loadbalancer.getLoadbalancerListenerBackRefs();
            if (listLoadBalancerListener != null && listLoadBalancerListener.size() > 0) {
                for (ObjectReference<ApiPropertyBase> listener : listLoadBalancerListener) {
                    LoadbalancerListener loadbalancerListener = (LoadbalancerListener) _tungstenApi.getTungstenObject(
                        LoadbalancerListener.class, listener.getUuid());
                    result = result && deleteLoadBalancerListener(loadbalancerListener);
                }
            }

            // delete load balancer
            result = result && _tungstenApi.deleteTungstenLoadBalancer(loadbalancer);

            // release floating ip
            result = result && _tungstenApi.releaseTungstenFloatingIp(cmd.getPublicNetworkUuid(), cmd.getFipName(),
                cmd.getFiName());

            // delete load balancer vmi
            VirtualMachineInterface virtualMachineInterface =
                (VirtualMachineInterface) _tungstenApi.getTungstenObjectByName(
                VirtualMachineInterface.class, project.getQualifiedName(), cmd.getLoadBalancerVmiName());

            result = result && _tungstenApi.deleteTungstenVmInterface(virtualMachineInterface);

            // delete load balancer health monitor
            LoadbalancerHealthmonitor loadbalancerHealthmonitor =
                (LoadbalancerHealthmonitor) _tungstenApi.getTungstenObjectByName(
                LoadbalancerHealthmonitor.class, project.getQualifiedName(), cmd.getLoadBalancerHealthMonitorName());
            result = result && _tungstenApi.deleteTungstenLoadBalancerHealthMonitor(loadbalancerHealthmonitor);

            if (result)
                return new TungstenAnswer(cmd, true, "Tungsten loadbalancer deleted");
            else {
                if (numRetries > 0) {
                    return retry(cmd, --numRetries);
                } else {
                    return new TungstenAnswer(cmd, new IOException());
                }
            }
        }
        return new TungstenAnswer(cmd, true, "Tungsten loadbalancer is not exist");
    }

    private Answer executeRequest(DeleteTungstenLoadBalancerListenerCommand cmd, int numRetries) {
        boolean result = true;
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        LoadbalancerListener loadbalancerListener = (LoadbalancerListener) _tungstenApi.getTungstenObjectByName(
            LoadbalancerListener.class, project.getQualifiedName(), cmd.getLoadBalancerListenerName());
        if (loadbalancerListener != null) {
            result = result && deleteLoadBalancerListener(loadbalancerListener);
            if (result)
                return new TungstenAnswer(cmd, true, "Tungsten loadbalancer listener deleted");
            else {
                if (numRetries > 0) {
                    return retry(cmd, --numRetries);
                } else {
                    return new TungstenAnswer(cmd, new IOException());
                }
            }
        }

        return new TungstenAnswer(cmd, true, "Tungsten loadbalancer listener is not exist");
    }

    private Answer executeRequest(UpdateTungstenLoadBalancerPoolCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        boolean result = _tungstenApi.updateLoadBalancerPool(project.getUuid(), cmd.getLbPoolName(), cmd.getLbMethod(),
            cmd.getLbSessionPersistence(), cmd.getLbPersistenceCookieName(), cmd.getLbProtocol(), cmd.isLbStatsEnable(),
            cmd.getLbStatsPort(), cmd.getLbStatsUri(), cmd.getLbStatsAuth());
        if (result)
            return new TungstenAnswer(cmd, true, "Tungsten loadbalancer pool updated");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(UpdateTungstenLoadBalancerListenerCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        boolean result = _tungstenApi.updateLoadBalancerListener(project.getUuid(), cmd.getListenerName(),
            cmd.getProtocol(), cmd.getPort(), cmd.getUrl());
        if (result)
            return new TungstenAnswer(cmd, true, "Tungsten loadbalancer listener updated");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(UpdateTungstenLoadBalancerMemberCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        String subnetUuid = _tungstenApi.getSubnetUuid(cmd.getNetworkUuid());
        if (subnetUuid == null) {
            return new TungstenAnswer(cmd, new IOException());
        }

        boolean result = _tungstenApi.updateLoadBalancerMember(project.getUuid(), cmd.getLbPoolName(),
            cmd.getListTungstenLoadBalancerMember(), subnetUuid);

        if (result)
            return new TungstenAnswer(cmd, true, "Tungsten loadbalancer member updated");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private boolean deleteLoadBalancerListener(LoadbalancerListener loadbalancerListener) {
        boolean result = true;
        List<ObjectReference<ApiPropertyBase>> listPool = loadbalancerListener.getLoadbalancerPoolBackRefs();
        if (listPool != null && listPool.size() > 0) {
            for (ObjectReference<ApiPropertyBase> pool : listPool) {
                LoadbalancerPool loadbalancerPool = (LoadbalancerPool) _tungstenApi.getTungstenObject(
                    LoadbalancerPool.class, pool.getUuid());
                List<ObjectReference<ApiPropertyBase>> listMember = loadbalancerPool.getLoadbalancerMembers();
                if (listMember != null && listMember.size() > 0) {
                    for (ObjectReference<ApiPropertyBase> member : listMember) {
                        LoadbalancerMember loadbalancerMember = (LoadbalancerMember) _tungstenApi.getTungstenObject(
                            LoadbalancerMember.class, member.getUuid());
                        result = result && _tungstenApi.deleteTungstenLoadBalancerMember(loadbalancerMember);
                    }
                }
                result = result && _tungstenApi.deleteTungstenLoadBalancerPool(loadbalancerPool);
            }
        }

        result = result && _tungstenApi.deleteTungstenLoadBalancerListener(loadbalancerListener);
        return result;
    }

    private Answer executeRequest(GetTungstenLoadBalancerCommand cmd, int numRetries) {
        Project project = (Project) _tungstenApi.getTungstenProjectByFqn(cmd.getProjectFqn());
        ApiObjectBase apiObjectBase = _tungstenApi.getTungstenObjectByName(Loadbalancer.class,
            project.getQualifiedName(), cmd.getLbName());
        if (apiObjectBase != null) {
            return new TungstenAnswer(cmd, apiObjectBase, true, "");
        } else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(ApplyTungstenPortForwardingCommand cmd, int numRetries) {
        boolean result = _tungstenApi.applyTungstenPortForwarding(cmd.isAdd(), cmd.getPublicNetworkUuid(),
            cmd.getFloatingIpPoolName(), cmd.getFloatingIpName(), cmd.getVmiUuid(), cmd.getProtocol(),
            cmd.getPublicPort(), cmd.getPrivatePort());

        if (result)
            return new TungstenAnswer(cmd, true, "Tungsten port forwarding floating ip enabled");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(DeleteTungstenObjectCommand cmd, int numRetries) {
        boolean result = _tungstenApi.deleteTungstenObject(cmd.getApiObjectBase());

        if (result)
            return new TungstenAnswer(cmd, true, "Deleted tungsten object");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(AddTungstenNetworkSubnetCommand cmd, int numRetries) {
        boolean result = _tungstenApi.addTungstenNetworkSubnetCommand(cmd.getNetworkUuid(), cmd.getIpPrefix(),
            cmd.getIpPrefixLen(), cmd.getGateway(), cmd.isDhcpEnable(), cmd.getDnsServer(), cmd.getAllocationStart(),
            cmd.getAllocationEnd(), cmd.isIpFromStart(), cmd.getSubnetName());

        if (result)
            return new TungstenAnswer(cmd, true, "tungsten network subnet is added");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer executeRequest(RemoveTungstenNetworkSubnetCommand cmd, int numRetries) {
        boolean result = _tungstenApi.removeTungstenNetworkSubnetCommand(cmd.getNetworkUuid(), cmd.getSubnetName());

        if (result)
            return new TungstenAnswer(cmd, true, "tungsten network subnet is deleted");
        else {
            if (numRetries > 0) {
                return retry(cmd, --numRetries);
            } else {
                return new TungstenAnswer(cmd, new IOException());
            }
        }
    }

    private Answer retry(Command cmd, int numRetries) {
        s_logger.warn("Retrying " + cmd.getClass().getSimpleName() + ". Number of retries remaining: " + numRetries);
        return executeRequest(cmd, numRetries);
    }

    @Override
    public void disconnected() {

    }

    @Override
    public boolean start() {
        return true;
    }

    @Override
    public boolean stop() {
        return true;
    }

    @Override
    public IAgentControl getAgentControl() {
        return null;
    }

    @Override
    public void setAgentControl(IAgentControl agentControl) {
    }

    private Answer executeRequest(ReadyCommand cmd) {
        return new ReadyAnswer(cmd);
    }

    private Answer executeRequest(MaintainCommand cmd) {
        return new MaintainAnswer(cmd);
    }

    private List<Subnet> getListSubnet(List<String> list) {
        List<Subnet> subnets = new ArrayList<>();
        for (String str : list) {
            String[] pair = StringUtils.split(str, "/");
            Subnet subnet = new Subnet(pair[0], Integer.parseInt(pair[1]));
            subnets.add(subnet);
        }
        return subnets;
    }

    @Override
    public void setName(final String name) {

    }

    @Override
    public void setConfigParams(final Map<String, Object> params) {

    }

    @Override
    public Map<String, Object> getConfigParams() {
        return null;
    }

    @Override
    public int getRunLevel() {
        return 0;
    }

    @Override
    public void setRunLevel(final int level) {

    }
}
