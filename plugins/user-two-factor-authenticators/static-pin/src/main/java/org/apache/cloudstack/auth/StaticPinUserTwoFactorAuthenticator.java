// Licensed to the Apache Software Foundation (ASF) under one or more
// contributor license agreements.  See the NOTICE file distributed with
// this work for additional information regarding copyright ownership.
// The ASF licenses this file to You under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with
// the License.  You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package org.apache.cloudstack.auth;

import javax.inject.Inject;

import com.cloud.exception.CloudAuthenticationException;
import com.cloud.user.UserAccount;
import org.apache.log4j.Logger;

import com.cloud.user.dao.UserAccountDao;
import com.cloud.utils.component.AdapterBase;

public class StaticPinUserTwoFactorAuthenticator extends AdapterBase implements UserTwoFactorAuthenticator {
    public static final Logger s_logger = Logger.getLogger(StaticPinUserTwoFactorAuthenticator.class);

    @Inject
    private UserAccountDao _userAccountDao;

    @Override
    public void check2FA(String code, UserAccount userAccount) throws CloudAuthenticationException  {
    }
}