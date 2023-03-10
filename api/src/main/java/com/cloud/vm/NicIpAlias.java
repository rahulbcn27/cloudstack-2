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
package com.cloud.vm;

import org.apache.cloudstack.acl.ControlledEntity;
import org.apache.cloudstack.api.Identity;
import org.apache.cloudstack.api.InternalIdentity;

/** Each entry represents the alias ip of a particular nic.
 *
 */
public interface NicIpAlias extends ControlledEntity, Identity, InternalIdentity {
    /**
     * @return id in the CloudStack database
     */
    enum State {
        active, revoked,
    }

    @Override
    long getId();

    long getNicId();

    String getIp4Address();

    String getIp6Address();

    long getNetworkId();

    long getVmId();

    Long getAliasCount();

    String getNetmask();

    String getGateway();

}
