#!/usr/bin/env python3
"""
User Agent与后端连接测试脚本
测试A2A协议通信和响应处理
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入A2A客户端
try:
    from python_a2a import A2AClient
    A2A_AVAILABLE = True
    print("✅ A2A客户端导入成功")
except ImportError as e:
    print(f"❌ A2A客户端导入失败: {e}")
    A2A_AVAILABLE = False

class UserAgentConnectionTester:
    """User Agent连接测试器"""
    
    def __init__(self):
        self.user_agent_url = "http://localhost:5011"
        self.backend_url = "http://localhost:5000"
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   详情: {details}")
        if response_time > 0:
            print(f"   响应时间: {response_time:.2f}秒")
        print()
    
    def test_user_agent_direct(self):
        """直接测试User Agent服务"""
        print("🔍 测试1: 直接连接User Agent...")
        
        if not A2A_AVAILABLE:
            self.log_test("User Agent直接连接", False, "A2A客户端不可用")
            return
        
        try:
            start_time = time.time()
            client = A2AClient(self.user_agent_url)
            response = client.ask("health check")
            response_time = time.time() - start_time
            
            if response and "healthy" in response.lower():
                self.log_test("User Agent直接连接", True, f"响应: {response[:100]}...", response_time)
            else:
                self.log_test("User Agent直接连接", False, f"异常响应: {response}")
                
        except Exception as e:
            self.log_test("User Agent直接连接", False, f"连接失败: {str(e)}")
    
    def test_backend_api(self):
        """测试后端API"""
        print("🔍 测试2: 后端API健康检查...")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("后端API健康检查", True, f"状态: {data.get('status', 'unknown')}", response_time)
            else:
                self.log_test("后端API健康检查", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("后端API健康检查", False, f"请求失败: {str(e)}")
    
    def test_backend_to_useragent(self):
        """测试后端通过A2A调用User Agent"""
        print("🔍 测试3: 后端→User Agent A2A通信...")
        
        test_message = "测试消息：请回复确认收到"
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json={"message": test_message, "user_id": "test_user"},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("后端→User Agent通信", True, 
                                f"响应: {data.get('response', '')[:100]}...", response_time)
                else:
                    self.log_test("后端→User Agent通信", False, 
                                f"API错误: {data.get('error', 'unknown')}")
            else:
                self.log_test("后端→User Agent通信", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("后端→User Agent通信", False, f"请求失败: {str(e)}")
    
    def test_shopping_request(self):
        """测试购物请求处理"""
        print("🔍 测试4: 购物请求处理...")
        
        shopping_message = "我想买一个iPhone 15 Pro"
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json={"message": shopping_message, "user_id": "test_user"},
                headers={"Content-Type": "application/json"},
                timeout=60  # 购物请求可能需要更长时间
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response_text = data.get('response', '')
                    # 检查是否包含商品信息
                    if any(keyword in response_text.lower() for keyword in ["iphone", "商品", "价格", "搜索"]):
                        self.log_test("购物请求处理", True, 
                                    f"包含商品信息，响应长度: {len(response_text)}", response_time)
                    else:
                        self.log_test("购物请求处理", False, 
                                    f"响应不包含预期商品信息: {response_text[:200]}...")
                else:
                    self.log_test("购物请求处理", False, 
                                f"API错误: {data.get('error', 'unknown')}")
            else:
                self.log_test("购物请求处理", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("购物请求处理", False, f"请求失败: {str(e)}")
    
    def test_agent_coordination(self):
        """测试Agent间协调功能"""
        print("🔍 测试5: Agent间协调功能...")
        
        if not A2A_AVAILABLE:
            self.log_test("Agent间协调", False, "A2A客户端不可用")
            return
        
        coordination_message = "确认购买iPhone 15 Pro，价格999美元"
        
        try:
            start_time = time.time()
            client = A2AClient(self.user_agent_url)
            response = client.ask(coordination_message)
            response_time = time.time() - start_time
            
            if response:
                # 检查是否包含协调相关的关键词
                coordination_keywords = ["支付", "订单", "确认", "payment", "order"]
                if any(keyword in response.lower() for keyword in coordination_keywords):
                    self.log_test("Agent间协调", True, 
                                f"包含协调信息，响应长度: {len(response)}", response_time)
                else:
                    self.log_test("Agent间协调", False, 
                                f"响应不包含协调信息: {response[:200]}...")
            else:
                self.log_test("Agent间协调", False, "空响应")
                
        except Exception as e:
            self.log_test("Agent间协调", False, f"调用失败: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始User Agent与后端连接测试...")
        print("=" * 60)
        
        # 运行所有测试
        self.test_user_agent_direct()
        self.test_backend_api()
        self.test_backend_to_useragent()
        self.test_shopping_request()
        self.test_agent_coordination()
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test_name']}: {result['details']}")
            print()
        
        print("💡 建议:")
        if failed_tests == 0:
            print("  🎉 所有测试通过！User Agent与后端连接正常。")
        else:
            print("  🔧 请检查失败的服务是否正常启动")
            print("  🔧 确认端口配置是否正确")
            print("  🔧 检查防火墙设置")
        
        # 保存详细报告
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"  📄 详细报告已保存到: {report_file}")

def main():
    """主函数"""
    tester = UserAgentConnectionTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
