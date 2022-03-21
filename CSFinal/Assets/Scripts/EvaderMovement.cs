using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;

public class EvaderMovement : MonoBehaviour
{
    public Animator animator;
    public bool grounded = false;
    Vector3 speed = new Vector3(0, 0, 0);
    public float xDir = 0;
    float moveSpeedRatio = 0.02f;
    float moveSpeedCap = 0.16f;
    float baseJumpSpeed = 0.25f;
    float footPos = 0;
    float gravity = 0.02f;
    bool jumped = false;
    int jumpTimer = 0;
    float terminalVelocity = -0.30f;
    public BoxCollider2D boxCollider2d;
    public Rigidbody2D rigidbody2D;
    public SpriteRenderer sprRend;
    void Start()
    {
        Rigidbody2D rigidbody2D = GetComponent<Rigidbody2D>();
        BoxCollider2D boxCollider2d = GetComponent<BoxCollider2D>();
        SpriteRenderer sprRend = GetComponent<SpriteRenderer>();

        float x_max = 572.5f;
        float x_min = 555.5f;
        float y = 309.0f;
        var section_width = 17.0f / 12.0f;
        var rand = new System.Random();
        float x = (((int)(UnityEngine.Random.value * 6) * section_width * 2) + section_width) + x_min;
        Vector3 startpos = new Vector3(x, y, 1.0f);
        transform.position = startpos;
    }
    
    
    void Update()
    {
        xDir = 0;
        //Input
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            xDir -= 1;
            sprRend.flipX = true;
        }
        if (Input.GetKey(KeyCode.RightArrow))
        {
            xDir += 1;
            sprRend.flipX = false;
        }
        if (Input.GetKeyDown(KeyCode.UpArrow) && grounded)
        {
            // Debug.Log("jump");
            jumped = true;
            speed.y = baseJumpSpeed;
            jumpTimer = 8;
        }
        if (Input.GetKeyUp(KeyCode.W))
        {
            jumpTimer = 0;
            jumped = false;
        }
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        grounded = IsGrounded(0.02f);
        animator.SetBool("grounded", grounded);
        if (jumped == true && jumpTimer > 0)
        {
            speed.y += 0.022f;
            jumpTimer--;
        }

        if (xDir == 0)
        {
            animator.SetBool("moving_x", false);
            if (grounded)
            {
                if (Math.Abs(speed.x) < 0.02)
                {
                    speed.x = 0;
                }
                else
                {
                    speed.x -= Math.Sign(speed.x) * 0.02f;
                }
            }
            else
            {
                if (Math.Abs(speed.x) < 0.005)
                {
                    speed.x = 0;
                }
                else
                {
                    speed.x -= Math.Sign(speed.x) * 0.005f;
                }
            }
        }
        else
        {
            animator.SetBool("moving_x", true);
        }
        if (Math.Abs(speed.x) < moveSpeedCap || Math.Sign(speed.x) != Math.Sign(xDir))
        {
            if (grounded)
            {
                speed.x += moveSpeedRatio * xDir;
            }
            else
            {
                speed.x += moveSpeedRatio /2 * xDir;
            }
        }
        Vector3 tmp = transform.position; 
        if (!grounded)
        {
            if (speed.y < 0)
            {
                speed.y -= gravity * 1.5f;
            }
            else
            {
                speed.y -= gravity;
            }
            
        }
        if (grounded && speed.y < 0)
        {
            //Debug.Log("hit ground");
            //tmp.y = (float)(Math.Round(tmp.y * 2f) / 2f);
            speed.y = 0f;
        }
        if (IsHittingCeiling())
        {
            speed.y = -0.05f;
        }

        if ((IsHittingLeftWall() && speed.x < 0) || (IsHittingRightWall() && speed.x > 0))
        {
            //Debug.Log("hit wall");
            speed.x = 0;
        }
        footPos = tmp.y - .5f;
        animator.SetFloat("y_speed", speed.y);
        rigidbody2D.MovePosition(tmp + speed);
    }

    public bool IsGrounded(float length)
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.down, length);
        return hit.collider != null;
    }
    public bool IsHittingCeiling()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.up, 0.01f);
        return hit.collider != null;
    }

    public bool IsHittingRightWall()
    {   
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.right, 0.02f);
        return hit.collider != null;
    }

    public bool IsHittingLeftWall()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.left, 0.02f);
        return hit.collider != null;
    }
}
