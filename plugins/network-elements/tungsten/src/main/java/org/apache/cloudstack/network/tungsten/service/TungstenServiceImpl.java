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
package org.apache.cloudstack.network.tungsten.service;

import com.cloud.network.IpAddress;
import com.cloud.network.IpAddressManager;
import com.cloud.network.Network;
import com.cloud.network.NetworkModel;
import com.cloud.network.Networks;
import com.cloud.network.TungstenProvider;
import com.cloud.network.dao.IPAddressDao;
import com.cloud.network.dao.IPAddressVO;
import com.cloud.network.dao.NetworkDao;
import com.cloud.network.dao.NetworkVO;
import com.cloud.network.dao.TungstenProviderDao;
import com.cloud.network.element.TungstenProviderVO;
import com.cloud.projects.ProjectVO;
import com.cloud.projects.dao.ProjectDao;
import com.cloud.user.Account;
import com.cloud.user.dao.AccountDao;
import com.cloud.utils.TungstenUtils;
import com.cloud.utils.component.ManagerBase;
import net.juniper.tungsten.api.types.FloatingIp;
import org.apache.cloudstack.framework.messagebus.MessageBus;
import org.apache.cloudstack.framework.messagebus.MessageSubscriber;
import org.apache.cloudstack.network.tungsten.agent.api.ApplyTungstenNetworkPolicyCommand;
import org.apache.cloudstack.network.tungsten.agent.api.CreateTungstenFloatingIpCommand;
import org.apache.cloudstack.network.tungsten.agent.api.DeleteTungstenFloatingIpCommand;
import org.apache.cloudstack.network.tungsten.agent.api.GetTungstenFloatingIpsCommand;
import org.apache.cloudstack.network.tungsten.agent.api.TungstenAnswer;
import org.apache.log4j.Logger;

import java.util.List;

import javax.inject.Inject;

public class TungstenServiceImpl extends ManagerBase implements TungstenService {
    private static final Logger s_logger = Logger.getLogger(TungstenServiceImpl.class);
    @Inject
    private MessageBus _messageBus;
    @Inject
    private ProjectDao _projectDao;
    @Inject
    private AccountDao _accountDao;
    @Inject
    private NetworkDao _networkDao;
    @Inject
    private IPAddressDao _ipAddressDao;
    @Inject
    protected NetworkModel _networkModel;
    @Inject
    private TungstenProviderDao _tungstenProviderDao;
    @Inject
    private TungstenFabricUtils _tungstenFabricUtils;

    @Override
    public boolean start() {
        synchronizeTungstenData();
        subcribeTungstenEvent();
        return super.start();
    }

    private void synchronizeTungstenData() {
        List<TungstenProviderVO> tungstenProviderList = _tungstenProviderDao.findAll();
        for (TungstenProviderVO tungstenProviderVO : tungstenProviderList) {
            long zoneId = tungstenProviderVO.getZoneId();
            Network publicNetwork = _networkModel.getSystemNetworkByZoneAndTrafficType(zoneId,
                Networks.TrafficType.Public);
            List<IPAddressVO> ipAddressList = _ipAddressDao.listByDcId(zoneId);
            for (IpAddress ipAddressVO : ipAddressList) {
                if (!ipAddressVO.isSourceNat() && ipAddressVO.getState() == IpAddress.State.Allocated) {
                    createTungstenFloatingIp(zoneId, ipAddressVO);
                }
            }
            deleteTungstenListFloatingIp(zoneId, publicNetwork);
        }
    }

    private boolean deleteTungstenListFloatingIp(long zoneId, Network publicNetwork) {
        boolean result = true;
        GetTungstenFloatingIpsCommand getTungstenFloatingIpsCommand = new GetTungstenFloatingIpsCommand(
            publicNetwork.getUuid(), TungstenUtils.getFloatingIpPoolName(zoneId));
        TungstenAnswer getFloatingIpsTungstenAnswer = _tungstenFabricUtils.sendTungstenCommand(
            getTungstenFloatingIpsCommand, zoneId);
        List<FloatingIp> floatingIpList = (List<FloatingIp>) getFloatingIpsTungstenAnswer.getApiObjectBaseList();
        for (FloatingIp floatingIp : floatingIpList) {
            IPAddressVO ipAddressVO = _ipAddressDao.findByIpAndDcId(zoneId, floatingIp.getAddress());
            if (!ipAddressVO.isSourceNat() && ipAddressVO.getState() == IpAddress.State.Free) {
                DeleteTungstenFloatingIpCommand deleteTungstenFloatingIpCommand = new DeleteTungstenFloatingIpCommand(
                    publicNetwork.getUuid(), TungstenUtils.getFloatingIpPoolName(zoneId),
                    TungstenUtils.getFloatingIpName(ipAddressVO.getId()));
                TungstenAnswer deleteFloatingIpTungstenAnswer = _tungstenFabricUtils.sendTungstenCommand(
                    deleteTungstenFloatingIpCommand, zoneId);
                result = result && deleteFloatingIpTungstenAnswer.getResult();
            }
        }
        return result;
    }

    private void subcribeTungstenEvent() {
        _messageBus.subscribe(IpAddressManager.MESSAGE_ASSIGN_IPADDR_EVENT, new MessageSubscriber() {
            @Override
            public void onPublishMessage(final String senderAddress, final String subject, final Object args) {
                try {
                    final IpAddress ipAddress = (IpAddress) args;
                    long zoneId = ipAddress.getDataCenterId();
                    TungstenProvider tungstenProvider = _tungstenProviderDao.findByZoneId(zoneId);
                    if (!ipAddress.isSourceNat() && tungstenProvider != null) {
                        createTungstenFloatingIp(zoneId, ipAddress);
                    }
                } catch (final Exception e) {
                    s_logger.error(e.getMessage());
                }
            }
        });

        _messageBus.subscribe(IpAddressManager.MESSAGE_RELEASE_IPADDR_EVENT, new MessageSubscriber() {
            @Override
            public void onPublishMessage(final String senderAddress, final String subject, final Object args) {
                try {
                    final IpAddress ipAddress = (IpAddress) args;
                    if (!ipAddress.isSourceNat() && ipAddress.getState() == IpAddress.State.Releasing) {
                        long zoneId = ipAddress.getDataCenterId();
                        TungstenProvider tungstenProvider = _tungstenProviderDao.findByZoneId(zoneId);
                        if (tungstenProvider != null) {
                            deleteTungstenFloatingIp(zoneId, ipAddress);
                        }
                    }
                } catch (final Exception e) {
                    s_logger.error(e.getMessage());
                }
            }
        });

        _messageBus.subscribe(TungstenService.MESSAGE_APPLY_NETWORK_POLICY_EVENT, new MessageSubscriber() {
            @Override
            public void onPublishMessage(final String senderAddress, final String subject, final Object args) {
                try {
                    final Network network = (Network) args;
                    List<IPAddressVO> ipAddressVOList = _ipAddressDao.listByAccount(Account.ACCOUNT_ID_SYSTEM);
                    for (IPAddressVO ipAddressVO : ipAddressVOList) {
                        ApplyTungstenNetworkPolicyCommand applyTungstenNetworkPolicyCommand =
                            new ApplyTungstenNetworkPolicyCommand(
                            null, TungstenUtils.getPublicNetworkPolicyName(ipAddressVO.getId()), network.getUuid(),
                            true);
                        _tungstenFabricUtils.sendTungstenCommand(applyTungstenNetworkPolicyCommand,
                            network.getDataCenterId());
                    }
                } catch (final Exception e) {
                    s_logger.error(e.getMessage());
                }
            }
        });
    }

    private boolean createTungstenFloatingIp(long zoneId, IpAddress ipAddress) {
        Network publicNetwork = _networkModel.getSystemNetworkByZoneAndTrafficType(zoneId, Networks.TrafficType.Public);
        String projectUuid = getProject(ipAddress.getAccountId());
        CreateTungstenFloatingIpCommand createTungstenFloatingIpPoolCommand = new CreateTungstenFloatingIpCommand(
            projectUuid, publicNetwork.getUuid(), TungstenUtils.getFloatingIpPoolName(zoneId),
            TungstenUtils.getFloatingIpName(ipAddress.getId()), ipAddress.getAddress().addr());
        TungstenAnswer tungstenAnswer = _tungstenFabricUtils.sendTungstenCommand(createTungstenFloatingIpPoolCommand,
            zoneId);
        return tungstenAnswer.getResult();
    }

    private void deleteTungstenFloatingIp(long zoneId, IpAddress ipAddress) {
        List<NetworkVO> publicNetworkVOList = _networkDao.listByZoneAndTrafficType(zoneId, Networks.TrafficType.Public);
        NetworkVO publicNetwork = publicNetworkVOList.get(0);
        DeleteTungstenFloatingIpCommand deleteTungstenFloatingIpPoolCommand = new DeleteTungstenFloatingIpCommand(
            publicNetwork.getUuid(), TungstenUtils.getFloatingIpPoolName(zoneId),
            TungstenUtils.getFloatingIpName(ipAddress.getId()));
        _tungstenFabricUtils.sendTungstenCommand(deleteTungstenFloatingIpPoolCommand, zoneId);
    }

    @Override
    public String getProject(long accountId) {
        Account account = _accountDao.findById(accountId);
        if (account.getType() == Account.ACCOUNT_TYPE_PROJECT) {
            ProjectVO projectVO = _projectDao.findByProjectAccountId(account.getId());
            if (projectVO != null) {
                return projectVO.getUuid();
            }
        }
        return null;
    }
}
