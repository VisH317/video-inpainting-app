import React from 'react'
import { View, Pressable } from 'react-native'
import modalStyles from './modalStyles'
import { PropsWithChildren } from 'react'

type props = PropsWithChildren<{
    open: boolean
    close: () => void
}>

export default function Modal({ children, open, close }: props) {
    return (
        <View style={open ? modalStyles.backdrop : modalStyles.invisible} onTouchEnd={close}>
            <View style={open ? modalStyles.modal : modalStyles.invisible} onStartShouldSetResponder={e => true} onTouchEnd={e => {console.log("e");e.stopPropagation()}}>
                {children}
            </View>
        </View>
    )
}