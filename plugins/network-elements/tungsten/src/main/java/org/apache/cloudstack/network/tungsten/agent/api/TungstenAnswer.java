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
package org.apache.cloudstack.network.tungsten.agent.api;

import com.cloud.agent.api.Answer;
import com.cloud.agent.api.Command;
import net.juniper.tungsten.api.ApiObjectBase;

import java.util.List;

public class TungstenAnswer extends Answer {

    ApiObjectBase apiObjectBase;
    List<? extends ApiObjectBase> apiObjectBaseList;

    public TungstenAnswer(final Command command, final boolean success, final String details) {
        super(command, success, details);
    }

    public TungstenAnswer(final Command command, ApiObjectBase apiObjectBase, final boolean success,
        final String details) {
        super(command, success, details);
        setApiObjectBase(apiObjectBase);
    }

    public TungstenAnswer(final Command command, List<? extends ApiObjectBase> apiObjectBaseList, final boolean success,
        final String details) {
        super(command, success, details);
        setApiObjectBaseList(apiObjectBaseList);
    }

    public TungstenAnswer(final Command command, final Exception e) {
        super(command, e);
    }

    public ApiObjectBase getApiObjectBase() {
        return apiObjectBase;
    }

    public void setApiObjectBase(ApiObjectBase apiObjectBase) {
        this.apiObjectBase = apiObjectBase;
    }

    public List<? extends ApiObjectBase> getApiObjectBaseList() {
        return apiObjectBaseList;
    }

    public void setApiObjectBaseList(final List<? extends ApiObjectBase> apiObjectBaseList) {
        this.apiObjectBaseList = apiObjectBaseList;
    }
}
