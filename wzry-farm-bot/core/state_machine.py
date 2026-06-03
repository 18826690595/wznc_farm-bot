"""
状态机 - 管理农场自动化状态流转
"""
from enum import Enum, auto
from loguru import logger
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass
import time


class FarmState(Enum):
    """农场状态枚举"""
    IDLE = auto()           # 空闲
    CONNECTING = auto()     # 连接中
    ENTERING = auto()       # 进入农场中
    HARVESTING = auto()     # 收菜中
    PLANTING = auto()       # 种菜中
    STEALING = auto()       # 偷菜中
    BLESSING = auto()       # 祝福中
    ERROR = auto()          # 错误状态
    STOPPED = auto()        # 已停止


@dataclass
class StateTransition:
    """状态转换记录"""
    from_state: FarmState
    to_state: FarmState
    timestamp: float
    message: str = ""


class StateMachine:
    """
    状态机
    管理农场自动化的状态流转
    """
    
    # 合法状态转换映射
    VALID_TRANSITIONS: Dict[FarmState, List[FarmState]] = {
        FarmState.IDLE: [
            FarmState.CONNECTING,
            FarmState.HARVESTING,
            FarmState.PLANTING,
            FarmState.STEALING,
            FarmState.BLESSING,
            FarmState.STOPPED
        ],
        FarmState.CONNECTING: [
            FarmState.IDLE,
            FarmState.ENTERING,
            FarmState.ERROR
        ],
        FarmState.ENTERING: [
            FarmState.IDLE,
            FarmState.HARVESTING,
            FarmState.ERROR
        ],
        FarmState.HARVESTING: [
            FarmState.IDLE,
            FarmState.PLANTING,
            FarmState.ERROR
        ],
        FarmState.PLANTING: [
            FarmState.IDLE,
            FarmState.STEALING,
            FarmState.ERROR
        ],
        FarmState.STEALING: [
            FarmState.IDLE,
            FarmState.BLESSING,
            FarmState.ERROR
        ],
        FarmState.BLESSING: [
            FarmState.IDLE,
            FarmState.ERROR
        ],
        FarmState.ERROR: [
            FarmState.IDLE,
            FarmState.STOPPED
        ],
        FarmState.STOPPED: []
    }
    
    def __init__(self):
        """初始化状态机"""
        self._state = FarmState.IDLE
        self._history: List[StateTransition] = []
        self._state_handlers: Dict[FarmState, Callable] = {}
        self._enter_callbacks: Dict[FarmState, List[Callable]] = {}
        self._exit_callbacks: Dict[FarmState, List[Callable]] = {}
        
        logger.info(f"状态机初始化，当前状态: {self._state.name}")
    
    @property
    def state(self) -> FarmState:
        """当前状态"""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._state not in [FarmState.IDLE, FarmState.STOPPED, FarmState.ERROR]
    
    @property
    def is_stopped(self) -> bool:
        """是否已停止"""
        return self._state == FarmState.STOPPED
    
    def can_transition_to(self, target: FarmState) -> bool:
        """
        检查是否可以转换到目标状态
        
        Args:
            target: 目标状态
            
        Returns:
            是否可以转换
        """
        valid_targets = self.VALID_TRANSITIONS.get(self._state, [])
        return target in valid_targets
    
    def transition_to(self, target: FarmState, message: str = "") -> bool:
        """
        转换到目标状态
        
        Args:
            target: 目标状态
            message: 转换消息
            
        Returns:
            是否转换成功
        """
        if not self.can_transition_to(target):
            logger.warning(
                f"非法状态转换: {self._state.name} -> {target.name}"
            )
            return False
        
        old_state = self._state
        self._state = target
        
        # 记录转换历史
        transition = StateTransition(
            from_state=old_state,
            to_state=target,
            timestamp=time.time(),
            message=message
        )
        self._history.append(transition)
        
        logger.info(f"状态转换: {old_state.name} -> {target.name}" + 
                   (f" ({message})" if message else ""))
        
        # 执行回调
        self._execute_exit_callbacks(old_state)
        self._execute_enter_callbacks(target)
        
        return True
    
    def register_handler(self, state: FarmState, handler: Callable):
        """
        注册状态处理器
        
        Args:
            state: 状态
            handler: 处理函数
        """
        self._state_handlers[state] = handler
        logger.debug(f"注册状态处理器: {state.name}")
    
    def register_enter_callback(self, state: FarmState, callback: Callable):
        """
        注册进入状态回调
        
        Args:
            state: 状态
            callback: 回调函数
        """
        if state not in self._enter_callbacks:
            self._enter_callbacks[state] = []
        self._enter_callbacks[state].append(callback)
    
    def register_exit_callback(self, state: FarmState, callback: Callable):
        """
        注册退出状态回调
        
        Args:
            state: 状态
            callback: 回调函数
        """
        if state not in self._exit_callbacks:
            self._exit_callbacks[state] = []
        self._exit_callbacks[state].append(callback)
    
    def _execute_enter_callbacks(self, state: FarmState):
        """执行进入状态回调"""
        callbacks = self._enter_callbacks.get(state, [])
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"执行进入回调失败: {e}")
    
    def _execute_exit_callbacks(self, state: FarmState):
        """执行退出状态回调"""
        callbacks = self._exit_callbacks.get(state, [])
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"执行退出回调失败: {e}")
    
    def execute_current_state(self) -> bool:
        """
        执行当前状态的处理器
        
        Returns:
            执行是否成功
        """
        handler = self._state_handlers.get(self._state)
        
        if handler is None:
            logger.debug(f"状态 {self._state.name} 没有注册处理器")
            return True
        
        try:
            return handler()
        except Exception as e:
            logger.error(f"执行状态处理器失败: {e}")
            self.transition_to(FarmState.ERROR, str(e))
            return False
    
    def get_history(self, limit: int = 10) -> List[StateTransition]:
        """
        获取状态转换历史
        
        Args:
            limit: 返回记录数量
            
        Returns:
            转换历史列表
        """
        return self._history[-limit:]
    
    def reset(self):
        """重置状态机"""
        self._state = FarmState.IDLE
        self._history.clear()
        logger.info("状态机已重置")
    
    def stop(self):
        """停止状态机"""
        if self._state != FarmState.STOPPED:
            self.transition_to(FarmState.STOPPED, "用户请求停止")
    
    def force_state(self, state: FarmState):
        """
        强制设置状态（用于错误恢复）
        
        Args:
            state: 目标状态
        """
        old_state = self._state
        self._state = state
        logger.warning(f"强制设置状态: {old_state.name} -> {state.name}")
