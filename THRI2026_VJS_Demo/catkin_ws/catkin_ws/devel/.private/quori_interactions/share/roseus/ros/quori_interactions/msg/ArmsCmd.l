;; Auto-generated. Do not edit!


(when (boundp 'quori_interactions::ArmsCmd)
  (if (not (find-package "QUORI_INTERACTIONS"))
    (make-package "QUORI_INTERACTIONS"))
  (shadow 'ArmsCmd (find-package "QUORI_INTERACTIONS")))
(unless (find-package "QUORI_INTERACTIONS::ARMSCMD")
  (make-package "QUORI_INTERACTIONS::ARMSCMD"))

(in-package "ROS")
;;//! \htmlinclude ArmsCmd.msg.html


(defclass quori_interactions::ArmsCmd
  :super ros::object
  :slots (_r_shoulder_pitch _r_shoulder_roll _l_shoulder_pitch _l_shoulder_roll _waist_pitch ))

(defmethod quori_interactions::ArmsCmd
  (:init
   (&key
    ((:r_shoulder_pitch __r_shoulder_pitch) 0.0)
    ((:r_shoulder_roll __r_shoulder_roll) 0.0)
    ((:l_shoulder_pitch __l_shoulder_pitch) 0.0)
    ((:l_shoulder_roll __l_shoulder_roll) 0.0)
    ((:waist_pitch __waist_pitch) 0.0)
    )
   (send-super :init)
   (setq _r_shoulder_pitch (float __r_shoulder_pitch))
   (setq _r_shoulder_roll (float __r_shoulder_roll))
   (setq _l_shoulder_pitch (float __l_shoulder_pitch))
   (setq _l_shoulder_roll (float __l_shoulder_roll))
   (setq _waist_pitch (float __waist_pitch))
   self)
  (:r_shoulder_pitch
   (&optional __r_shoulder_pitch)
   (if __r_shoulder_pitch (setq _r_shoulder_pitch __r_shoulder_pitch)) _r_shoulder_pitch)
  (:r_shoulder_roll
   (&optional __r_shoulder_roll)
   (if __r_shoulder_roll (setq _r_shoulder_roll __r_shoulder_roll)) _r_shoulder_roll)
  (:l_shoulder_pitch
   (&optional __l_shoulder_pitch)
   (if __l_shoulder_pitch (setq _l_shoulder_pitch __l_shoulder_pitch)) _l_shoulder_pitch)
  (:l_shoulder_roll
   (&optional __l_shoulder_roll)
   (if __l_shoulder_roll (setq _l_shoulder_roll __l_shoulder_roll)) _l_shoulder_roll)
  (:waist_pitch
   (&optional __waist_pitch)
   (if __waist_pitch (setq _waist_pitch __waist_pitch)) _waist_pitch)
  (:serialization-length
   ()
   (+
    ;; float32 _r_shoulder_pitch
    4
    ;; float32 _r_shoulder_roll
    4
    ;; float32 _l_shoulder_pitch
    4
    ;; float32 _l_shoulder_roll
    4
    ;; float32 _waist_pitch
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; float32 _r_shoulder_pitch
       (sys::poke _r_shoulder_pitch (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _r_shoulder_roll
       (sys::poke _r_shoulder_roll (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _l_shoulder_pitch
       (sys::poke _l_shoulder_pitch (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _l_shoulder_roll
       (sys::poke _l_shoulder_roll (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _waist_pitch
       (sys::poke _waist_pitch (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; float32 _r_shoulder_pitch
     (setq _r_shoulder_pitch (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _r_shoulder_roll
     (setq _r_shoulder_roll (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _l_shoulder_pitch
     (setq _l_shoulder_pitch (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _l_shoulder_roll
     (setq _l_shoulder_roll (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _waist_pitch
     (setq _waist_pitch (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;;
   self)
  )

(setf (get quori_interactions::ArmsCmd :md5sum-) "18963acf222a3961918de358f517947a")
(setf (get quori_interactions::ArmsCmd :datatype-) "quori_interactions/ArmsCmd")
(setf (get quori_interactions::ArmsCmd :definition-)
      "float32 r_shoulder_pitch
float32 r_shoulder_roll
float32 l_shoulder_pitch
float32 l_shoulder_roll
float32 waist_pitch

")



(provide :quori_interactions/ArmsCmd "18963acf222a3961918de358f517947a")


